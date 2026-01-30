from unittest.mock import AsyncMock, Mock

import pytest

from src.application.referral.stats import (
    GetStatsInteractor,
    GetTopReferrersInteractor,
    StatsOutputDTO,
    TopReferrerDTO,
)
from src.domain.user.repository import ReferralStats, TopReferrer


class TestGetStatsInteractor:
    @pytest.fixture
    def user_repository(self) -> Mock:
        return Mock()

    @pytest.fixture
    def interactor(self, user_repository: Mock) -> GetStatsInteractor:
        return GetStatsInteractor(user_repository=user_repository)

    async def test_returns_stats(
        self, interactor: GetStatsInteractor, user_repository: Mock
    ) -> None:
        user_repository.get_referral_stats = AsyncMock(
            return_value=ReferralStats(
                total_users=100,
                referred_count=40,
                organic_count=60,
            )
        )

        result = await interactor()

        assert isinstance(result, StatsOutputDTO)
        assert result.total_users == 100
        assert result.referred_count == 40
        assert result.referred_percent == 40.0
        assert result.organic_count == 60
        assert result.organic_percent == 60.0

    async def test_handles_zero_users(
        self, interactor: GetStatsInteractor, user_repository: Mock
    ) -> None:
        user_repository.get_referral_stats = AsyncMock(
            return_value=ReferralStats(
                total_users=0,
                referred_count=0,
                organic_count=0,
            )
        )

        result = await interactor()

        assert result.referred_percent == 0
        assert result.organic_percent == 0


class TestGetTopReferrersInteractor:
    @pytest.fixture
    def user_repository(self) -> Mock:
        return Mock()

    @pytest.fixture
    def interactor(self, user_repository: Mock) -> GetTopReferrersInteractor:
        return GetTopReferrersInteractor(user_repository=user_repository)

    async def test_returns_top_referrers(
        self, interactor: GetTopReferrersInteractor, user_repository: Mock
    ) -> None:
        user_repository.get_top_referrers = AsyncMock(
            return_value=[
                TopReferrer(
                    user_id=1, username="user1", first_name="John", referral_count=10
                ),
                TopReferrer(
                    user_id=2, username=None, first_name="Jane", referral_count=5
                ),
            ]
        )

        result = await interactor(10)

        assert len(result) == 2
        assert isinstance(result[0], TopReferrerDTO)
        assert result[0].count == 10
        assert result[1].username is None
