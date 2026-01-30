from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from src.application.referral.get_info import (
    GetReferralInfoInteractor,
    ReferralInfoOutputDTO,
)
from src.domain.user import User
from src.domain.user.vo import FirstName, ReferralCount, UserId


class TestGetReferralInfoInteractor:
    @pytest.fixture
    def mock_user_repository(self):
        return Mock()

    @pytest.fixture
    def interactor(self, mock_user_repository):
        return GetReferralInfoInteractor(user_repository=mock_user_repository)

    @pytest.fixture
    def sample_user(self):
        now = datetime.now(UTC)
        return User(
            id=UserId(123456789),
            first_name=FirstName("John"),
            last_name=None,
            username=None,
            bio=None,
            created_at=now,
            updated_at=now,
            last_login_at=now,
            referred_by=None,
            referral_count=ReferralCount(5),
        )

    async def test_returns_referral_info(
        self, interactor, mock_user_repository, sample_user
    ):
        mock_user_repository.get_user = AsyncMock(return_value=sample_user)

        result = await interactor(123456789)

        assert isinstance(result, ReferralInfoOutputDTO)
        assert result.referral_count == 5
        assert len(result.referral_code) == 8

    async def test_referral_code_is_deterministic(
        self, interactor, mock_user_repository, sample_user
    ):
        mock_user_repository.get_user = AsyncMock(return_value=sample_user)

        result1 = await interactor(123456789)
        result2 = await interactor(123456789)

        assert result1.referral_code == result2.referral_code

    async def test_user_not_found_raises(self, interactor, mock_user_repository):
        mock_user_repository.get_user = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="User not found"):
            await interactor(999)
