from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.repos import UserRepositoryImpl


class HolderDao:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepositoryImpl(session)
