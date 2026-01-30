from dataclasses import dataclass

from src.application.common.interactor import Interactor
from src.application.common.transaction import TransactionManager
from src.application.user.service import UpsertUserData, UserService


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
    is_new: bool = False


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

        return CreateUserOutputDTO(
            id=user.id.value,
            username=user.username.value if user.username else None,
            first_name=user.first_name.value,
            last_name=user.last_name.value if user.last_name else None,
            is_new=user.is_new,
        )
