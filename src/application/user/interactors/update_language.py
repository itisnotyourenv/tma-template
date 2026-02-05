from dataclasses import dataclass

from src.application.common.interactor import Interactor
from src.application.common.transaction import TransactionManager
from src.domain.user import UserRepository
from src.domain.user.vo import LanguageCode, UserId


@dataclass(frozen=True)
class UpdateLanguageDTO:
    user_id: UserId
    language_code: LanguageCode


class UpdateLanguageInteractor(Interactor[UpdateLanguageDTO, None]):
    def __init__(
        self,
        user_repository: UserRepository,
        transaction_manager: TransactionManager,
    ) -> None:
        self._user_repository = user_repository
        self._transaction_manager = transaction_manager

    async def __call__(self, data: UpdateLanguageDTO) -> None:
        await self._user_repository.update_language(
            user_id=data.user_id,
            language_code=data.language_code,
        )
        await self._transaction_manager.commit()
