"""Middleware for loading user and i18n."""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.types import User as AiogramUser
from dishka import AsyncContainer
from dishka.integrations.aiogram import CONTAINER_NAME
from fluentogram import TranslatorHub

from src.application.user.create import CreateUserInteractor
from src.application.user.dtos import (
    CreateUserInputDTO,
    CreateUserOutputDTO,
)
from src.presentation.bot.utils.i18n import extract_language_code


class UserAndLocaleMiddleware(BaseMiddleware):
    """Middleware that loads and injects user and i18n.

    Adds `user` (or None) and `i18n` to handler data dict.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:  # noqa: ANN401
        from_user: AiogramUser | None = getattr(event, "from_user", None)
        if from_user is None:
            return await handler(event, data)

        container: AsyncContainer = data[CONTAINER_NAME]
        upsert_interactor = await container.get(CreateUserInteractor)
        hub = await container.get(TranslatorHub)

        # Create or update user
        user_dto: CreateUserOutputDTO = await upsert_interactor(
            data=CreateUserInputDTO(
                id=from_user.id,
                username=from_user.username,
                first_name=from_user.first_name,
                last_name=from_user.last_name,
            )
        )

        # Get locale: prefer saved language, fallback to Telegram language
        if user_dto.language_code:
            locale = user_dto.language_code
        else:
            locale = extract_language_code(from_user.language_code)

        data["user"] = user_dto
        data["i18n"] = hub.get_translator_by_locale(locale)

        return await handler(event, data)
