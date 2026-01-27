from typing import TypedDict


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
