from dataclasses import dataclass

from src.application.common.interactor import Interactor
from src.domain.user import UserRepository
from src.domain.user.services.referral import encode_referral
from src.domain.user.vo import UserId


@dataclass
class GetReferralInfoInputDTO:
    user_id: int


@dataclass
class GetReferralInfoOutputDTO:
    referral_code: str
    referral_count: int


class GetReferralInfoInteractor(
    Interactor[GetReferralInfoInputDTO, GetReferralInfoOutputDTO | None]
):
    def __init__(
        self,
        user_repository: UserRepository,
        secret_key: str,
    ) -> None:
        self.user_repository = user_repository
        self.secret_key = secret_key

    async def __call__(
        self, data: GetReferralInfoInputDTO
    ) -> GetReferralInfoOutputDTO | None:
        user = await self.user_repository.get_user(UserId(data.user_id))

        if user is None:
            return None

        return GetReferralInfoOutputDTO(
            referral_code=encode_referral(data.user_id, self.secret_key),
            referral_count=user.referral_count.value if user.referral_count else 0,
        )
