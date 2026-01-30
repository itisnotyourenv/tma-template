from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from src.application.referral.get_info import (
    GetReferralInfoInputDTO,
    GetReferralInfoInteractor,
    GetReferralInfoOutputDTO,
)
from src.domain.user import User
from src.domain.user.services.referral import decode_referral
from src.domain.user.vo import FirstName, ReferralCount, UserId


@pytest.fixture
def secret_key() -> str:
    return "test-secret"


@pytest.fixture
def user_repository() -> Mock:
    return Mock()


@pytest.fixture
def interactor(user_repository: Mock, secret_key: str) -> GetReferralInfoInteractor:
    return GetReferralInfoInteractor(
        user_repository=user_repository,
        secret_key=secret_key,
    )


@pytest.fixture
def sample_user() -> User:
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


class TestGetReferralInfoInteractor:
    async def test_returns_referral_info(
        self,
        interactor: GetReferralInfoInteractor,
        user_repository: Mock,
        sample_user: User,
        secret_key: str,
    ) -> None:
        user_repository.get_user = AsyncMock(return_value=sample_user)

        result = await interactor(GetReferralInfoInputDTO(user_id=123456789))

        assert isinstance(result, GetReferralInfoOutputDTO)
        assert result.referral_count == 5
        # Verify code is decodable
        decoded = decode_referral(result.referral_code, secret_key)
        assert decoded == 123456789

    async def test_user_not_found_returns_none(
        self,
        interactor: GetReferralInfoInteractor,
        user_repository: Mock,
    ) -> None:
        user_repository.get_user = AsyncMock(return_value=None)

        result = await interactor(GetReferralInfoInputDTO(user_id=999))

        assert result is None
