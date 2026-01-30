from dataclasses import dataclass

from src.application.common.interactor import Interactor
from src.application.common.transaction import TransactionManager
from src.application.user.service import UpsertUserData, UserService
from src.domain.user import UserRepository
from src.domain.user.vo import UserId


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
        user_repository: UserRepository,
        transaction_manager: TransactionManager,
    ) -> None:
        self.user_service = user_service
        self.user_repository = user_repository
        self.transaction_manager = transaction_manager

    async def __call__(self, data: CreateUserInputDTO) -> CreateUserOutputDTO:
        # Check if user exists to determine is_new
        existing_user = await self.user_repository.get_user(UserId(data.id))
        is_new = existing_user is None

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
            is_new=is_new,
        )
