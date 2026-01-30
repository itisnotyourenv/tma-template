from dataclasses import dataclass

from src.application.common.interactor import Interactor
from src.application.common.transaction import TransactionManager
from src.domain.user import UserRepository
from src.domain.user.services.referral import find_referrer_id
from src.domain.user.vo import UserId


@dataclass
class ProcessReferralInputDTO:
    new_user_id: int
    referral_code: str


class ProcessReferralInteractor(Interactor[ProcessReferralInputDTO, bool]):
    def __init__(
        self,
        user_repository: UserRepository,
        transaction_manager: TransactionManager,
    ) -> None:
        self.user_repository = user_repository
        self.transaction_manager = transaction_manager

    async def __call__(self, data: ProcessReferralInputDTO) -> bool:
        user_ids = await self.user_repository.get_all_user_ids()
        referrer_id = find_referrer_id(data.referral_code, user_ids)

        if referrer_id is None:
            return False

        if referrer_id == data.new_user_id:
            return False

        await self.user_repository.set_referred_by(
            UserId(data.new_user_id), UserId(referrer_id)
        )
        await self.user_repository.increment_referral_count(UserId(referrer_id))
        await self.transaction_manager.commit()

        return True
