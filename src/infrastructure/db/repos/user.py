from datetime import UTC, datetime
from typing import Unpack

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from src.domain.user.entity import User
from src.domain.user.repository import CreateUserDTO, UpdateUserDTO, UserRepository
from src.domain.user.vo import UserId, Username
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

        return user_model.to_domain() if user_model else None

    async def create_user(self, user: CreateUserDTO) -> User:
        stmt = (
            insert(UserModel)
            .values(
                id=user["id"],
                username=user["username"],
                first_name=user["first_name"],
                last_name=user["last_name"],
            )
            .returning(UserModel)
        )

        result = await self._session.execute(stmt)
        orm_model = result.scalar_one()
        return orm_model.to_domain()

    async def update_user(
        self, user_id: UserId, **fields: Unpack[UpdateUserDTO]
    ) -> User:
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(
                username=fields["username"],
                first_name=fields["first_name"],
                last_name=fields["last_name"],
                last_login_at=datetime.now(UTC),
            )
            .returning(UserModel)
        )
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one()
        return orm_model.to_domain()

    async def delete_user(self, user_id: UserId) -> None:
        raise NotImplementedError
