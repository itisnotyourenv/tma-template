from sqlalchemy.ext.asyncio import AsyncSession


class BaseSQLAlchemyRepo:
    def __init__(self, session: AsyncSession):
        self._session = session
