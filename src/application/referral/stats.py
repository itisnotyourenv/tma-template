from dataclasses import dataclass

from src.application.common.interactor import Interactor
from src.domain.user import UserRepository


@dataclass
class StatsOutputDTO:
    total_users: int
    referred_count: int
    referred_percent: float
    organic_count: int
    organic_percent: float


class GetStatsInteractor(Interactor[None, StatsOutputDTO]):
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def __call__(self, data: None = None) -> StatsOutputDTO:
        stats = await self.user_repository.get_referral_stats()

        if stats.total_users > 0:
            referred_pct = stats.referred_count / stats.total_users * 100
            organic_pct = stats.organic_count / stats.total_users * 100
        else:
            referred_pct = 0
            organic_pct = 0

        return StatsOutputDTO(
            total_users=stats.total_users,
            referred_count=stats.referred_count,
            referred_percent=round(referred_pct, 1),
            organic_count=stats.organic_count,
            organic_percent=round(organic_pct, 1),
        )


@dataclass
class TopReferrerDTO:
    user_id: int
    username: str | None
    first_name: str
    count: int


class GetTopReferrersInteractor(Interactor[int, list[TopReferrerDTO]]):
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def __call__(self, data: int = 10) -> list[TopReferrerDTO]:
        top = await self.user_repository.get_top_referrers(limit=data)

        return [
            TopReferrerDTO(
                user_id=r.user_id,
                username=r.username,
                first_name=r.first_name,
                count=r.referral_count,
            )
            for r in top
        ]
