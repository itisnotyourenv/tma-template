from collections.abc import AsyncGenerator
from typing import Any

from aiogram import Bot
from aiogram.client.session.base import BaseSession
from aiogram.methods import (
    AnswerCallbackQuery,
    DeleteMessage,
    EditMessageReplyMarkup,
    EditMessageText,
    SendMessage,
    TelegramMethod,
)
from aiogram.methods.base import TelegramType
from aiogram.types import Chat, Message


class NoOpSession(BaseSession):
    """Fake session that intercepts all Telegram API calls.

    Returns valid objects so aiogram deserialization doesn't fail.
    """

    async def make_request(
        self,
        bot: Bot,
        method: TelegramMethod[TelegramType],
        timeout: int | None = None,
    ) -> TelegramType | None:
        if isinstance(method, AnswerCallbackQuery | DeleteMessage):
            return True

        if isinstance(method, SendMessage | EditMessageText | EditMessageReplyMarkup):
            return Message(
                message_id=1,
                date=0,
                chat=Chat(id=0, type="private"),
            )

        return True

    async def close(self) -> None:
        pass

    async def stream_content(
        self,
        url: str,
        headers: dict[str, Any] | None = None,
        timeout: int = 30,
        chunk_size: int = 65536,
        raise_for_status: bool = True,
    ) -> AsyncGenerator[bytes]:
        yield b""
