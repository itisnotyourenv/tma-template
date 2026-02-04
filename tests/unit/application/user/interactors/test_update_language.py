from unittest.mock import AsyncMock

import pytest

from src.application.user.interactors.update_language import (
    UpdateLanguageDTO,
    UpdateLanguageInteractor,
)
from src.domain.user.vo import LanguageCode, UserId


class TestUpdateLanguageInteractor:
    @pytest.fixture
    def mock_user_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_transaction_manager(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def interactor(
        self, mock_user_repository: AsyncMock, mock_transaction_manager: AsyncMock
    ) -> UpdateLanguageInteractor:
        return UpdateLanguageInteractor(
            user_repository=mock_user_repository,
            transaction_manager=mock_transaction_manager,
        )

    async def test_update_language_calls_repository(
        self,
        interactor: UpdateLanguageInteractor,
        mock_user_repository: AsyncMock,
        mock_transaction_manager: AsyncMock,
    ) -> None:
        user_id = UserId(123456)
        language_code = LanguageCode("ru")

        await interactor(
            UpdateLanguageDTO(user_id=user_id, language_code=language_code)
        )

        mock_user_repository.update_language.assert_called_once_with(
            user_id=user_id, language_code=language_code
        )

    async def test_update_language_commits_transaction(
        self,
        interactor: UpdateLanguageInteractor,
        mock_transaction_manager: AsyncMock,
    ) -> None:
        user_id = UserId(123456)
        language_code = LanguageCode("en")

        await interactor(
            UpdateLanguageDTO(user_id=user_id, language_code=language_code)
        )

        mock_transaction_manager.commit.assert_called_once()

    async def test_update_language_returns_none(
        self,
        interactor: UpdateLanguageInteractor,
    ) -> None:
        user_id = UserId(123456)
        language_code = LanguageCode("en")

        result = await interactor(
            UpdateLanguageDTO(user_id=user_id, language_code=language_code)
        )

        assert result is None
