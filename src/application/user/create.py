from src.application.common.interactor import Interactor
from src.application.common.transaction import TransactionManager
from src.application.user.dtos import (
    CreateUserInputDTO,
    CreateUserOutputDTO,
    entity_to_dto,
)
from src.application.user.service import UpsertUserData, UserService


class CreateUserInteractor(Interactor[CreateUserInputDTO, CreateUserOutputDTO]):
    def __init__(
        self,
        user_service: UserService,
        transaction_manager: TransactionManager,
    ) -> None:
        self.user_service = user_service
        self.transaction_manager = transaction_manager

    async def __call__(self, data: CreateUserInputDTO) -> CreateUserOutputDTO:
        user = await self.user_service.upsert_user(
            UpsertUserData(
                id=data.id,
                username=data.username,
                first_name=data.first_name,
                last_name=data.last_name,
            )
        )

        await self.transaction_manager.commit()

        return entity_to_dto(user)
