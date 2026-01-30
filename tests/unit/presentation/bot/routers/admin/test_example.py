from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import Message, User
from fluentogram import TranslatorHub

from src.infrastructure.i18n import create_translator_hub
from src.presentation.bot.routers.admin.example import example_admin_handler


class TestExampleAdminHandler:
    @pytest.fixture
    def hub(self) -> TranslatorHub:
        locales_dir = (
            Path(__file__).parent.parent.parent.parent.parent.parent.parent / "locales"
        )
        return create_translator_hub(locales_dir)

    @pytest.fixture
    def mock_message(self) -> MagicMock:
        message = MagicMock(spec=Message)
        message.from_user = MagicMock(spec=User)
        message.from_user.language_code = "en"
        message.answer = AsyncMock()
        return message

    def _create_mock_container(self, hub: TranslatorHub) -> MagicMock:
        """Create a mock Dishka container that resolves dependencies."""
        container = MagicMock()

        async def mock_get(dep_type: type, **kwargs: object) -> object:
            if dep_type is TranslatorHub:
                return hub
            raise ValueError(f"Unknown dependency: {dep_type}")

        container.get = mock_get
        return container

    async def test_example_handler_uses_english(
        self, mock_message: MagicMock, hub: TranslatorHub
    ) -> None:
        mock_container = self._create_mock_container(hub)

        await example_admin_handler(
            mock_message,
            dishka_container=mock_container,
        )

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args
        assert call_args.kwargs["text"] == "Example admin command executed"

    async def test_example_handler_uses_russian_for_ru_user(
        self, mock_message: MagicMock, hub: TranslatorHub
    ) -> None:
        mock_message.from_user.language_code = "ru"

        mock_container = self._create_mock_container(hub)

        await example_admin_handler(
            mock_message,
            dishka_container=mock_container,
        )

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args
        assert call_args.kwargs["text"] == "Пример админской команды выполнен"
