from dataclasses import dataclass

from src.application.common.interactor import Interactor
from src.application.common.transaction import TransactionManager
from src.application.interfaces.auth import AuthService
from src.domain.user import (
    CreateUserDTO,
    UserRepository,
)
from src.domain.user.vo import UserId


@dataclass
class CreateUserInputDTO:
    id: int
    username: str | None
    first_name: str
    last_name: str | None
    is_premium: bool
    photo_url: str | None


@dataclass
class CreateUserOutputDTO:
    id: int
    username: str | None
    first_name: str
    last_name: str | None


class CreateUserInteractor(Interactor[CreateUserInputDTO, CreateUserOutputDTO]):
    def __init__(
        self,
        user_repository: UserRepository,
        transaction_manager: TransactionManager,
        auth_service: AuthService,
    ) -> None:
        self.user_repository = user_repository
        self.transaction_manager = transaction_manager
        self.auth_service = auth_service

    async def __call__(self, data: CreateUserInputDTO) -> CreateUserOutputDTO:
        user_id = UserId(data.id)

        user = await self.user_repository.get_user(user_id)

        if user is None:
            user = await self.user_repository.create_user(
                CreateUserDTO(
                    id=data.id,
                    username=data.username,
                    first_name=data.first_name,
                    last_name=data.last_name,
                    is_premium=data.is_premium,
                    photo_url=data.photo_url,
                ),
            )
        else:
            user = await self.user_repository.update_user(
                user_id=user_id,
                username=data.username,
                first_name=data.first_name,
                last_name=data.last_name,
                is_premium=data.is_premium,
                photo_url=data.photo_url,
            )

        await self.transaction_manager.commit()

        return CreateUserOutputDTO(
            id=user.id.value,
            username=user.username.value if user.username else None,
            first_name=user.first_name.value,
            last_name=user.last_name.value if user.last_name else None,
        )
