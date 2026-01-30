from dataclasses import dataclass

from src.application.common.interactor import Interactor
from src.domain.user import UserRepository
from src.domain.user.services.referral import generate_referral_code
from src.domain.user.vo import UserId


@dataclass
class ReferralInfoOutputDTO:
    referral_code: str
    referral_count: int


class GetReferralInfoInteractor(Interactor[int, ReferralInfoOutputDTO]):
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def __call__(self, user_id: int) -> ReferralInfoOutputDTO:
        user = await self.user_repository.get_user(UserId(user_id))

        if user is None:
            raise ValueError("User not found")

        referral_code = generate_referral_code(user_id)
        referral_count = user.referral_count.value if user.referral_count else 0

        return ReferralInfoOutputDTO(
            referral_code=referral_code,
            referral_count=referral_count,
        )
