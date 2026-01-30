from dataclasses import dataclass

from src.application.common.interactor import Interactor
from src.application.common.transaction import TransactionManager
from src.application.interfaces.auth import AuthService
from src.application.user.service import UpsertUserData, UserService


@dataclass
class AuthTgInputDTO:
    init_data: str


@dataclass
class AuthTgOutputDTO:
    access_token: str


class AuthTgInteractor(Interactor[AuthTgInputDTO, AuthTgOutputDTO]):
    def __init__(
        self,
        user_service: UserService,
        transaction_manager: TransactionManager,
        auth_service: AuthService,
    ) -> None:
        self.user_service = user_service
        self.transaction_manager = transaction_manager
        self.auth_service = auth_service

    async def __call__(self, data: AuthTgInputDTO) -> AuthTgOutputDTO:
        parsed_data = self.auth_service.validate_init_data(data.init_data)

        await self.user_service.upsert_user(
            UpsertUserData(
                id=parsed_data.user_id,
                username=parsed_data.username,
                first_name=parsed_data.first_name,
                last_name=parsed_data.last_name,
            )
        )

        await self.transaction_manager.commit()

        access_token = self.auth_service.create_access_token(
            parsed_data.user_id,
        )
        return AuthTgOutputDTO(
            access_token=access_token,
        )
