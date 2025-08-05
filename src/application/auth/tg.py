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
class AuthTgInputDTO:
    init_data: str


@dataclass
class AuthTgOutputDTO:
    access_token: str


class AuthTgInteractor(Interactor[AuthTgInputDTO, AuthTgOutputDTO]):
    def __init__(
        self,
        user_repository: UserRepository,
        transaction_manager: TransactionManager,
        auth_service: AuthService,
    ) -> None:
        self.user_repository = user_repository
        self.transaction_manager = transaction_manager
        self.auth_service = auth_service

    async def __call__(self, data: AuthTgInputDTO) -> AuthTgOutputDTO:
        parsed_data = self.auth_service.validate_init_data(data.init_data)

        user = await self.user_repository.get_user(UserId(parsed_data.user_id))
        if user is None:
            await self.user_repository.create_user(
                CreateUserDTO(
                    id=parsed_data.user_id,
                    username=parsed_data.username,
                    first_name=parsed_data.first_name,
                    last_name=parsed_data.last_name,
                    is_premium=parsed_data.is_premium,
                    photo_url=parsed_data.photo_url,
                ),
            )
        else:
            await self.user_repository.update_user(
                user_id=UserId(parsed_data.user_id),
                username=parsed_data.username,
                first_name=parsed_data.first_name,
                last_name=parsed_data.last_name,
                is_premium=parsed_data.is_premium,
                photo_url=parsed_data.photo_url,
            )

        await self.transaction_manager.commit()

        access_token = self.auth_service.create_access_token(
            parsed_data.user_id,
        )
        return AuthTgOutputDTO(
            access_token=access_token,
        )
