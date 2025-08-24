import os
from collections.abc import AsyncGenerator, AsyncIterator, Callable

import httpx
import pytest
from dishka import AsyncContainer, make_async_container
from dishka.integrations.litestar import setup_dishka
from httpx import AsyncClient
from litestar import Litestar
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.domain.user.vo import UserId
from src.infrastructure.config import Config
from src.infrastructure.db.models.base import BaseORMModel
from src.infrastructure.di import (
    AuthProvider,
    DBProvider,
    interactor_providers,
)
from src.presentation.api.app import prepare_app


def get_worker_database_url(base_url: str) -> str:
    """Generate worker-specific database URL for parallel test execution."""
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")

    # Parse the base URL to extract components
    if "://" not in base_url:
        raise ValueError(f"Invalid database URL format: {base_url}")

    protocol, rest = base_url.split("://", 1)

    # Split the rest into user:password@host:port/database
    if "@" in rest:
        auth_part, host_db_part = rest.rsplit("@", 1)
    else:
        auth_part = ""
        host_db_part = rest

    if "/" in host_db_part:
        host_port, database = host_db_part.rsplit("/", 1)
    else:
        host_port = host_db_part
        database = ""

    # Create worker-specific database name
    worker_db = database if worker_id == "master" else f"{database}_{worker_id}"

    # Reconstruct the URL
    if auth_part:
        return f"{protocol}://{auth_part}@{host_port}/{worker_db}"
    else:
        return f"{protocol}://{host_port}/{worker_db}"


async def create_worker_database(base_url: str, worker_url: str) -> None:
    """Create worker-specific database if it doesn't exist."""
    if base_url == worker_url:
        # Master worker uses the original database, no need to create
        return

    # Extract database name from worker URL
    worker_db_name = worker_url.split("/")[-1]

    # Create engine connected to the main database to create worker database
    main_db_url = base_url.rsplit("/", 1)[0] + "/postgres"  # Connect to postgres db
    main_engine = create_async_engine(
        main_db_url, echo=False, isolation_level="AUTOCOMMIT"
    )

    try:
        async with main_engine.connect() as conn:
            # Check if database exists
            result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": worker_db_name},
            )

            if not result.fetchone():
                # Create the worker database
                await conn.execute(text(f'CREATE DATABASE "{worker_db_name}"'))
    finally:
        await main_engine.dispose()


@pytest.fixture(scope="session")
def test_app(test_config: Config) -> Litestar:
    app = prepare_app(test_config)
    app.debug = True
    return app


@pytest.fixture(scope="function")
def app(dishka_container_for_tests: AsyncContainer, test_app: Litestar) -> Litestar:
    setup_dishka(dishka_container_for_tests, test_app)
    return test_app


@pytest.fixture(scope="function")
async def test_client(app: Litestar):
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=True)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver.local",
    ) as client:
        yield client


@pytest.fixture(scope="function")
def create_authenticated_client(
    test_client: AsyncClient,
) -> Callable[..., tuple[AsyncClient, UserId]]:
    """Factory to create authenticated clients for tests."""

    def _create_authenticated_client(user_id: int) -> tuple[AsyncClient, UserId]:
        client = test_client
        client.headers.update({"X-User-Id": str(user_id)})
        return client, UserId(user_id)

    return _create_authenticated_client


@pytest.fixture
def authenticated_client(create_authenticated_client) -> tuple[AsyncClient, UserId]:
    """Set up test client with authentication headers."""
    return create_authenticated_client(1)


@pytest.fixture(scope="session")
async def dishka_container_for_tests(
    test_config: Config,
    sqlalchemy_engine: AsyncEngine,
) -> AsyncGenerator[AsyncContainer]:
    await clear_db_data(sqlalchemy_engine)

    # Create worker-specific config for database isolation
    worker_db_url = get_worker_database_url(test_config.postgres.url)
    worker_db_name = worker_db_url.split("/")[-1]

    # Create a modified postgres config with worker-specific database name
    worker_postgres_config = test_config.postgres.model_copy(
        update={"db": worker_db_name}
    )
    worker_config = test_config.model_copy(update={"postgres": worker_postgres_config})

    interactor_provider_instances = [
        interactor() for interactor in interactor_providers
    ]

    container = make_async_container(
        AuthProvider(),
        DBProvider(worker_postgres_config),
        *interactor_provider_instances,
        context={Config: worker_config},
    )
    yield container
    await container.close()


@pytest.fixture(scope="session")
async def sqlalchemy_engine(test_config: Config) -> AsyncGenerator[AsyncEngine]:
    # Get worker-specific database URL
    worker_db_url = get_worker_database_url(test_config.postgres.url)

    # Create engine with worker-specific database
    engine = create_async_engine(worker_db_url, echo=False)

    # Create the worker-specific database if it doesn't exist
    await create_worker_database(test_config.postgres.url, worker_db_url)

    # Set up schema in the worker database
    await setup_db_schema(engine)

    yield engine
    await engine.dispose(close=True)


async def setup_db_schema(sqlalchemy_engine: AsyncEngine) -> None:
    """Create database schema once per session."""
    async with sqlalchemy_engine.begin() as conn:
        await conn.run_sync(BaseORMModel.metadata.create_all)


async def clear_db_data(sqlalchemy_engine: AsyncEngine) -> None:
    """Fast database cleanup using table truncation instead of schema recreation."""
    async with sqlalchemy_engine.begin() as conn:
        # Get all table names from metadata
        tables = list(BaseORMModel.metadata.tables.keys())

        if tables:
            # Disable foreign key checks for faster truncation
            await conn.execute(text("SET session_replication_role = replica;"))

            # Truncate all tables
            for table in tables:
                await conn.execute(
                    text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")
                )

            # Re-enable foreign key checks
            await conn.execute(text("SET session_replication_role = DEFAULT;"))


@pytest.fixture(scope="function")
async def db_session(
    dishka_container_for_tests: AsyncContainer,
) -> AsyncGenerator[AsyncSession]:
    async with dishka_container_for_tests() as container:
        session = await container.get(AsyncSession)
        yield session


@pytest.fixture(scope="session")
def async_session_maker(
    sqlalchemy_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(sqlalchemy_engine, expire_on_commit=False)


@pytest.fixture(scope="function")
async def native_db_session(
    sqlalchemy_engine: AsyncEngine,
    async_session_maker: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    await clear_db_data(sqlalchemy_engine)
    async with async_session_maker() as session:
        yield session
