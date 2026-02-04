"""Middleware for loading user and i18n."""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from dishka import AsyncContainer
from dishka.integrations.aiogram import CONTAINER_NAME
from fluentogram import TranslatorHub

from src.domain.user import User, UserRepository
from src.domain.user.vo import UserId
from src.presentation.bot.utils.i18n import extract_language_code


class UserAndLocaleMiddleware(BaseMiddleware):
    """Middleware that loads user and injects i18n.

    Adds `user` (or None) and `i18n` to handler data dict.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:  # noqa: ANN401
        from_user = getattr(event, "from_user", None)
        if from_user is None:
            return await handler(event, data)

        container: AsyncContainer = data[CONTAINER_NAME]
        user_repository = await container.get(UserRepository)
        hub = await container.get(TranslatorHub)

        # Load user from DB (may be None for new users)
        user: User | None = await user_repository.get_user(UserId(from_user.id))

        # Get locale: prefer saved language, fallback to Telegram language
        if user and user.language_code:
            locale = user.language_code.value
        else:
            locale = extract_language_code(from_user.language_code)

        data["user"] = user
        data["i18n"] = hub.get_translator_by_locale(locale)

        return await handler(event, data)
