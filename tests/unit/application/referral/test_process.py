from unittest.mock import AsyncMock, Mock

import pytest

from src.application.referral.process import (
    ProcessReferralInputDTO,
    ProcessReferralInteractor,
)
from src.domain.user.entity import User
from src.domain.user.services.referral import encode_referral


@pytest.fixture
def secret_key() -> str:
    return "test-secret-key"


@pytest.fixture
def user_repository() -> Mock:
    return Mock()


@pytest.fixture
def transaction_manager() -> Mock:
    manager = Mock()
    manager.commit = AsyncMock()
    return manager


@pytest.fixture
def interactor(
    user_repository: Mock,
    transaction_manager: Mock,
    secret_key: str,
) -> ProcessReferralInteractor:
    return ProcessReferralInteractor(
        user_repository=user_repository,
        transaction_manager=transaction_manager,
        secret_key=secret_key,
    )


class TestProcessReferralInteractor:
    async def test_valid_referral_sets_referred_by(
        self,
        interactor: ProcessReferralInteractor,
        user_repository: Mock,
        secret_key: str,
    ) -> None:
        referrer_id = 100
        new_user_id = 200
        code = encode_referral(referrer_id, secret_key)

        referrer = Mock(spec=User)
        user_repository.get_user = AsyncMock(return_value=referrer)
        user_repository.set_referred_by = AsyncMock()
        user_repository.increment_referral_count = AsyncMock()

        result = await interactor(
            ProcessReferralInputDTO(new_user_id=new_user_id, referral_code=code)
        )

        assert result is True
        user_repository.set_referred_by.assert_called_once()

    async def test_invalid_code_returns_false(
        self,
        interactor: ProcessReferralInteractor,
    ) -> None:
        result = await interactor(
            ProcessReferralInputDTO(new_user_id=200, referral_code="invalid!")
        )

        assert result is False

    async def test_self_referral_returns_false(
        self,
        interactor: ProcessReferralInteractor,
        secret_key: str,
    ) -> None:
        user_id = 100
        code = encode_referral(user_id, secret_key)

        result = await interactor(
            ProcessReferralInputDTO(new_user_id=user_id, referral_code=code)
        )

        assert result is False

    async def test_nonexistent_referrer_returns_false(
        self,
        interactor: ProcessReferralInteractor,
        user_repository: Mock,
        secret_key: str,
    ) -> None:
        code = encode_referral(100, secret_key)
        user_repository.get_user = AsyncMock(return_value=None)

        result = await interactor(
            ProcessReferralInputDTO(new_user_id=200, referral_code=code)
        )

        assert result is False
