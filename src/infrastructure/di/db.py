from collections.abc import AsyncIterable

from dishka import Provider, Scope, from_context, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.application.common.transaction import TransactionManager
from src.domain.admin import AdminRepository
from src.domain.user import UserRepository
from src.infrastructure.config import Config
from src.infrastructure.db.factory import create_engine, create_session_maker
from src.infrastructure.db.holder import HolderDao
from src.infrastructure.db.transaction import TransactionManagerImpl


class DBProvider(Provider):
    scope = Scope.APP

    config = from_context(provides=Config)

    @provide(scope=Scope.APP)
    async def get_engine(self, config: Config) -> AsyncIterable[AsyncEngine]:
        engine = create_engine(config.postgres)
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

    @provide(scope=Scope.REQUEST)
    async def get_admin_repository(
        self,
        holder_dao: HolderDao,
    ) -> AdminRepository:
        return holder_dao.admin_repo
