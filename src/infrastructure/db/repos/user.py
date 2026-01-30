from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from src.domain.user.entity import User
from src.domain.user.repository import UserRepository
from src.domain.user.vo import UserId, Username
from src.infrastructure.db.mappers import UserMapper
from src.infrastructure.db.models.user import UserModel
from src.infrastructure.db.repos.base import BaseSQLAlchemyRepo


class UserRepositoryImpl(UserRepository, BaseSQLAlchemyRepo):
    async def get_user(self, identifier: UserId | Username) -> User | None:
        if isinstance(identifier, UserId):
            stmt = select(UserModel).where(UserModel.id == identifier)
        else:  # by == "username"
            stmt = select(UserModel).where(UserModel.username == identifier)

        result = await self._session.execute(stmt)

        user_model = result.scalars().first()

        return UserMapper.to_domain(user_model) if user_model else None

    async def create_user(self, user: User) -> User:
        stmt = (
            insert(UserModel)
            .values(
                id=user.id.value,
                username=user.username.value if user.username else None,
                first_name=user.first_name.value,
                last_name=user.last_name.value if user.last_name else None,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login_at=user.last_login_at,
            )
            .returning(UserModel)
        )

        result = await self._session.execute(stmt)
        orm_model = result.scalar_one()
        return UserMapper.to_domain(orm_model)

    async def update_user(self, user: User) -> User:
        stmt = (
            update(UserModel)
            .where(UserModel.id == user.id.value)
            .values(
                username=user.username.value if user.username else None,
                first_name=user.first_name.value,
                last_name=user.last_name.value if user.last_name else None,
                updated_at=user.updated_at,
                last_login_at=user.last_login_at,
            )
            .returning(UserModel)
        )
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one()
        return UserMapper.to_domain(orm_model)

    async def delete_user(self, user_id: UserId) -> None:
        raise NotImplementedError
