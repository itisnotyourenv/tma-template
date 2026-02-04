"""Aiogram middleware for internationalization."""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from dishka import AsyncContainer
from fluentogram import TranslatorHub

from src.domain.user import UserRepository
from src.domain.user.vo import UserId
from src.presentation.bot.utils.i18n import extract_language_code


class I18nMiddleware(BaseMiddleware):
    """Middleware that injects localized translator into handler data."""

    def __init__(self, hub: TranslatorHub) -> None:
        """Initialize middleware with TranslatorHub.

        Args:
            hub: TranslatorHub instance for getting localized translators.
        """
        self.hub = hub
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:  # noqa: ANN401
        """Inject i18n translator into handler data."""
        locale = await self._get_locale(event, data)
        data["i18n"] = self.hub.get_translator_by_locale(locale)
        return await handler(event, data)

    async def _get_locale(self, event: TelegramObject, data: dict[str, Any]) -> str:
        """Get locale from DB or fallback to Telegram language."""
        from_user = getattr(event, "from_user", None)
        if from_user is None:
            return "en"

        # Try to get language from DB
        container: AsyncContainer | None = data.get("dishka_container")
        if container:
            try:
                user_repo = await container.get(UserRepository)
                user = await user_repo.get_user(UserId(from_user.id))
                if user and user.language_code:
                    return user.language_code.value
            except Exception:  # noqa: S110
                pass

        # Fallback to Telegram language
        return extract_language_code(from_user.language_code)
