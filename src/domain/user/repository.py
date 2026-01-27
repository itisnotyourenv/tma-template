from abc import abstractmethod
from typing import Protocol, overload

from src.domain.user.entity import User
from src.domain.user.vo import UserId, Username


class UserRepository(Protocol):
    @overload
    async def get_user(self, identifier: UserId) -> User | None: ...

    @overload
    async def get_user(self, identifier: Username) -> User | None: ...

    @abstractmethod
    async def get_user(self, identifier: UserId | Username) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def create_user(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def update_user(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def delete_user(self, user_id: UserId) -> None: ...
