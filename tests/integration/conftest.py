from collections.abc import Callable
from typing import AsyncGenerator

import httpx
import pytest
from dishka import AsyncContainer, Provider, Scope, make_async_container
from dishka.integrations.litestar import setup_dishka
from httpx import AsyncClient
from litestar import Litestar

from src.domain.user.vo import UserId
from src.infrastructure.config import Config
from src.presentation.api.app import prepare_app


@pytest.fixture(scope="session")
def test_app() -> Litestar:
    app = prepare_app()
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


@pytest.fixture(scope="function")
async def dishka_container_for_tests(
    test_config: Config,
) -> AsyncGenerator[AsyncContainer, None]:
    mock_provider = Provider(scope=Scope.APP)

    container = make_async_container(
        context={Config: test_config},
    )
    yield container
    await container.close()
