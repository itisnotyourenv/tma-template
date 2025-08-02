from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.infrastructure.config import PostgresConfig


def create_pool(db_config: PostgresConfig) -> async_sessionmaker[AsyncSession]:
    engine = create_engine(db_config)
    return create_session_maker(engine)


def create_engine(
    db_config: PostgresConfig,
    pool_size: int = 30,
    pool_timeout: int = 30,
    pool_recycle: int = 3600,
    max_overflow: int = 20,
) -> AsyncEngine:
    return create_async_engine(
        url=make_url(db_config.url),
        echo=db_config.echo,
        pool_size=pool_size,
        pool_timeout=pool_timeout,
        pool_recycle=pool_recycle,
        max_overflow=max_overflow,
    )


def create_session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    pool: async_sessionmaker[AsyncSession] = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
    )
    return pool
