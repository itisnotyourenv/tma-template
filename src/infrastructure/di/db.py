from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.application.common.transaction import TransactionManager
from src.domain.user import UserRepository
from src.infrastructure.config import PostgresConfig
from src.infrastructure.db.factory import create_engine, create_session_maker
from src.infrastructure.db.holder import HolderDao
from src.infrastructure.db.transaction import TransactionManagerImpl


class DBProvider(Provider):
    scope = Scope.APP

    def __init__(self, config: PostgresConfig) -> None:
        self.config = config
        super().__init__()

    @provide(scope=Scope.APP)
    async def get_engine(self) -> AsyncIterable[AsyncEngine]:
        engine = create_engine(self.config)
        yield engine
        await engine.dispose(close=True)

    @provide(scope=Scope.APP)
    def get_session_maker(
        self,
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        return create_session_maker(engine)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self,
        session_maker: async_sessionmaker[AsyncSession],
    ) -> AsyncIterable[AsyncSession]:
        async with session_maker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    async def get_holder_dao(
        self,
        session: AsyncSession,
    ) -> HolderDao:
        return HolderDao(session)

    @provide(scope=Scope.REQUEST)
    async def get_transaction_manager(
        self,
        session: AsyncSession,
    ) -> TransactionManager:
        return TransactionManagerImpl(session)

    @provide(scope=Scope.REQUEST)
    async def get_user_repository(
        self,
        holder_dao: HolderDao,
    ) -> UserRepository:
        return holder_dao.user_repo
