from unittest.mock import AsyncMock, Mock

import pytest

from src.application.referral.process import (
    ProcessReferralInputDTO,
    ProcessReferralInteractor,
)
from src.domain.user.services.referral import generate_referral_code
from src.domain.user.vo import UserId


class TestProcessReferralInteractor:
    @pytest.fixture
    def mock_user_repository(self):
        return Mock()

    @pytest.fixture
    def mock_transaction_manager(self):
        return Mock()

    @pytest.fixture
    def interactor(self, mock_user_repository, mock_transaction_manager):
        return ProcessReferralInteractor(
            user_repository=mock_user_repository,
            transaction_manager=mock_transaction_manager,
        )

    async def test_process_valid_referral(
        self, interactor, mock_user_repository, mock_transaction_manager
    ):
        referrer_id = 123
        new_user_id = 456
        code = generate_referral_code(referrer_id)

        mock_user_repository.get_all_user_ids = AsyncMock(
            return_value=[111, referrer_id, 222]
        )
        mock_user_repository.set_referred_by = AsyncMock()
        mock_user_repository.increment_referral_count = AsyncMock()
        mock_transaction_manager.commit = AsyncMock()

        input_dto = ProcessReferralInputDTO(
            new_user_id=new_user_id,
            referral_code=code,
        )

        result = await interactor(input_dto)

        assert result is True
        mock_user_repository.set_referred_by.assert_awaited_once_with(
            UserId(new_user_id), UserId(referrer_id)
        )
        mock_user_repository.increment_referral_count.assert_awaited_once_with(
            UserId(referrer_id)
        )
        mock_transaction_manager.commit.assert_awaited_once()

    async def test_referrer_not_found(
        self, interactor, mock_user_repository, mock_transaction_manager
    ):
        mock_user_repository.get_all_user_ids = AsyncMock(return_value=[111, 222])
        mock_transaction_manager.commit = AsyncMock()

        input_dto = ProcessReferralInputDTO(
            new_user_id=456,
            referral_code="unknown1",
        )

        result = await interactor(input_dto)

        assert result is False
        mock_user_repository.set_referred_by.assert_not_called()
        mock_user_repository.increment_referral_count.assert_not_called()

    async def test_self_referral_ignored(
        self, interactor, mock_user_repository, mock_transaction_manager
    ):
        user_id = 123
        code = generate_referral_code(user_id)

        mock_user_repository.get_all_user_ids = AsyncMock(return_value=[user_id])

        input_dto = ProcessReferralInputDTO(
            new_user_id=user_id,  # same as referrer
            referral_code=code,
        )

        result = await interactor(input_dto)

        assert result is False
        mock_user_repository.set_referred_by.assert_not_called()
