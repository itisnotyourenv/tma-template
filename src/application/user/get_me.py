from dataclasses import dataclass

from src.application.common.interactor import Interactor
from src.domain.user import (
    UserRepository,
)
from src.domain.user.vo import UserId


@dataclass
class GetUserProfileInputDTO:
    user_id: UserId


@dataclass
class GetUserProfileOutputDTO:
    id: int
    username: str
    first_name: str
    last_name: str


class GetUserProfileInteractor(
    Interactor[GetUserProfileInputDTO, GetUserProfileOutputDTO]
):
    def __init__(
        self,
        user_repository: UserRepository,
    ) -> None:
        self.user_repository = user_repository

    async def __call__(self, data: GetUserProfileInputDTO) -> GetUserProfileOutputDTO:
        user = await self.user_repository.get_user(data.user_id)

        if not user:
            raise NotImplementedError

        return GetUserProfileOutputDTO(
            id=user.id.value,
            username=user.username.value if user.username else None,
            first_name=user.first_name.value,
            last_name=user.last_name.value if user.last_name else None,
        )
