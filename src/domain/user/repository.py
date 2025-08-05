from abc import abstractmethod
from typing import Literal, Protocol, TypedDict, Unpack, overload

from src.domain.user.entity import User


class CreateUserDTO(TypedDict):
    id: int
    username: str | None
    first_name: str
    last_name: str | None
    is_premium: bool
    photo_url: str


class UpdateUserDTO(TypedDict):
    username: str | None
    first_name: str
    last_name: str | None
    is_premium: bool
    photo_url: str


class UserRepository(Protocol):
    @overload
    async def get_user(self, identifier: str) -> User | None: ...

    @overload
    async def get_user(
        self, identifier: int, by: str = Literal["id"]
    ) -> User | None: ...

    @overload
    async def get_user(
        self, identifier: str, by: str = Literal["username"]
    ) -> User | None: ...

    @abstractmethod
    async def get_user(
        self, identifier: int | str, by: Literal["id", "username"] = "id"
    ) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def create_user(self, user: CreateUserDTO) -> User:
        raise NotImplementedError

    @abstractmethod
    async def update_user(self, user_id: int, **fields: Unpack[UpdateUserDTO]) -> User:
        raise NotImplementedError

    async def delete_user(self, user_id: str) -> None: ...
