from dataclasses import dataclass

from src.domain.user import User


@dataclass
class CreateUserInputDTO:
    id: int
    username: str | None
    first_name: str
    last_name: str | None


@dataclass
class CreateUserOutputDTO:
    id: int
    username: str | None
    first_name: str
    last_name: str | None
    language_code: str | None = None
    is_new: bool = False


def entity_to_dto(user: User) -> CreateUserOutputDTO:
    return CreateUserOutputDTO(
        id=user.id.value,
        username=user.username.value if user.username else None,
        first_name=user.first_name.value,
        last_name=user.last_name.value if user.last_name else None,
        language_code=user.language_code.value if user.language_code else None,
        is_new=user.is_new,
    )
