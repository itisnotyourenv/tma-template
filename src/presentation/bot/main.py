import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError
from dishka import make_async_container
from dishka.integrations.aiogram import setup_dishka

from src.infrastructure.config import Config, load_config
from src.infrastructure.di import AuthProvider, DBProvider, interactor_providers
from src.presentation.bot.routers import setup_routers


async def notify_admins_on_startup(bot: Bot, config: Config) -> None:
    """Send notification to admins when bot starts up."""
    for admin_id in config.telegram.admin_ids:
        try:
            await bot.send_message(chat_id=admin_id, text="Bot has started!")
        except TelegramAPIError as e:
            logging.warning("Failed to notify admin %s: %s", admin_id, e)


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

    dp = Dispatcher()
    main_router = setup_routers()
    dp.include_router(main_router)

    container = make_async_container(
        AuthProvider(),
        DBProvider(config.postgres),  # todo - pass config with context
        *interactor_provider_instances,
        context={Config: config},
    )
    setup_dishka(container=container, router=dp)

    # Notify admins on startup
    await notify_admins_on_startup(bot, config)

    # And the run events dispatching
    await dp.start_polling(bot, config=config)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
