from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.filters import CommandObject
from aiogram.types import Message, User
from fluentogram import TranslatorHub

from src.application.referral.process import ProcessReferralInteractor
from src.application.user.create import CreateUserInteractor
from src.infrastructure.i18n import create_translator_hub
from src.presentation.bot.routers.commands import command_start_handler


class TestCommandStartHandler:
    @pytest.fixture
    def hub(self) -> TranslatorHub:
        locales_dir = (
            Path(__file__).parent.parent.parent.parent.parent.parent / "locales"
        )
        return create_translator_hub(locales_dir)

    @pytest.fixture
    def mock_message(self) -> MagicMock:
        message = MagicMock(spec=Message)
        message.from_user = MagicMock(spec=User)
        message.from_user.id = 123456
        message.from_user.username = "testuser"
        message.from_user.first_name = "John"
        message.from_user.last_name = "Doe"
        message.from_user.is_premium = False
        message.from_user.language_code = "en"
        message.answer = AsyncMock()
        return message

    @pytest.fixture
    def mock_command(self) -> MagicMock:
        command = MagicMock(spec=CommandObject)
        command.args = None
        return command

    def _create_mock_container(
        self, interactor: AsyncMock, process_referral: AsyncMock, hub: TranslatorHub
    ) -> MagicMock:
        """Create a mock Dishka container that resolves dependencies."""
        container = MagicMock()

        async def mock_get(dep_type: type, **kwargs: object) -> object:
            if dep_type is CreateUserInteractor:
                return interactor
            if dep_type is ProcessReferralInteractor:
                return process_referral
            if dep_type is TranslatorHub:
                return hub
            raise ValueError(f"Unknown dependency: {dep_type}")

        container.get = mock_get
        return container

    async def test_start_handler_uses_english_for_en_user(
        self, mock_message: MagicMock, mock_command: MagicMock, hub: TranslatorHub
    ) -> None:
        mock_interactor = AsyncMock()
        mock_interactor.return_value = MagicMock(first_name="John", is_new=False)
        mock_process_referral = AsyncMock()

        mock_container = self._create_mock_container(
            mock_interactor, mock_process_referral, hub
        )

        await command_start_handler(
            mock_message,
            mock_command,
            dishka_container=mock_container,
        )

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args
        assert call_args.kwargs["text"] == "Hello, \u2068John\u2069!"

    async def test_start_handler_uses_russian_for_ru_user(
        self, mock_message: MagicMock, mock_command: MagicMock, hub: TranslatorHub
    ) -> None:
        mock_message.from_user.language_code = "ru"
        mock_interactor = AsyncMock()
        mock_interactor.return_value = MagicMock(first_name="Иван", is_new=False)
        mock_process_referral = AsyncMock()

        mock_container = self._create_mock_container(
            mock_interactor, mock_process_referral, hub
        )

        await command_start_handler(
            mock_message,
            mock_command,
            dishka_container=mock_container,
        )

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args
        assert call_args.kwargs["text"] == "Привет, \u2068Иван\u2069!"  # noqa: RUF001

    async def test_start_handler_defaults_to_english_for_unknown_language(
        self, mock_message: MagicMock, mock_command: MagicMock, hub: TranslatorHub
    ) -> None:
        mock_message.from_user.language_code = "de"  # German not supported
        mock_interactor = AsyncMock()
        mock_interactor.return_value = MagicMock(first_name="Hans", is_new=False)
        mock_process_referral = AsyncMock()

        mock_container = self._create_mock_container(
            mock_interactor, mock_process_referral, hub
        )

        await command_start_handler(
            mock_message,
            mock_command,
            dishka_container=mock_container,
        )

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args
        assert call_args.kwargs["text"] == "Hello, \u2068Hans\u2069!"
