import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from dishka import make_async_container
from dishka.integrations.aiogram import FromDishka, inject, setup_dishka

from src.application.user.create import CreateUserInputDTO, CreateUserInteractor
from src.infrastructure.config import Config, load_config
from src.infrastructure.di import AuthProvider, DBProvider, interactor_providers

dp = Dispatcher()


@dp.message(CommandStart())
@inject
async def command_start_handler(
    message: Message, interactor: FromDishka[CreateUserInteractor]
) -> None:
    """
    This handler receives messages with `/start` command
    """
    user = await interactor(
        data=CreateUserInputDTO(
            id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            is_premium=message.from_user.is_premium,
            photo_url=None,
        )
    )

    msg = f"Hello, {user.first_name}!"
    await message.answer(text=msg)


@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


async def main() -> None:
    config = load_config()
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(
        token=config.telegram.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    interactor_provider_instances = [
        interactor() for interactor in interactor_providers
    ]

    container = make_async_container(
        AuthProvider(),
        DBProvider(config.postgres),  # todo - pass config with context
        *interactor_provider_instances,
        context={Config: config},
    )
    setup_dishka(container=container, router=dp)

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
