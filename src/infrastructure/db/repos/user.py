from typing import Literal, Unpack

from sqlalchemy.exc import NoResultFound
from sqlalchemy import select

from src.domain.user.entity import User
from src.domain.user.repository import UserRepository, UpdateUserDTO
from src.infrastructure.db.models.user import UserModel
from src.infrastructure.db.repos.base import BaseSQLAlchemyRepo


class UserRepositoryImpl(UserRepository, BaseSQLAlchemyRepo):
    async def get_user(
        self, identifier: str, by: Literal["id", "username"] = "id"
    ) -> User:
        if by == "id":
            stmt = select(UserModel).where(UserModel.id == identifier)
        else:  # by == "username"
            stmt = select(UserModel).where(UserModel.username == identifier)

        result = await self._session.execute(stmt)

        user_model = result.scalars().first()

        if user_model is None:
            raise NoResultFound(f"User not found with {by}: {identifier}")

        return user_model.to_domain()

    async def create_user(self, user: User) -> User:
        user_model = UserModel.from_domain(user)
        self._session.add(user_model)
        self._session.flush()
        self._session.refresh(user_model)
        return user_model.to_domain()

    async def update_user(self, user_id: int, **fields: Unpack[UpdateUserDTO]) -> User:
        pass
