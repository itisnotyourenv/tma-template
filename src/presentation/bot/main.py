import asyncio
from contextlib import suppress
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError
from dishka import make_async_container
from dishka.integrations.aiogram import setup_dishka

from src.infrastructure.config import Config, load_config
from src.infrastructure.di import (
    AuthProvider,
    DBProvider,
    I18nProvider,
    interactor_providers,
)
from src.infrastructure.i18n import DEFAULT_LANGUAGE, TranslatorHub
from src.presentation.bot.middleware.user_and_locale import UserAndLocaleMiddleware
from src.presentation.bot.routers import setup_routers


async def notify_admins_on_startup(
    bot: Bot, config: Config, hub: TranslatorHub
) -> None:
    """Send notification to admins when bot starts up."""
    i18n = hub.get_translator_by_locale(DEFAULT_LANGUAGE)
    for admin_id in config.telegram.admin_ids:
        try:
            await bot.send_message(chat_id=admin_id, text=i18n.bot_started())
        except TelegramAPIError as ex:
            logging.warning("Failed to notify admin %s: %s", admin_id, ex)


async def main() -> None:
    config = load_config()
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
        DBProvider(),
        I18nProvider(),
        *interactor_provider_instances,
        context={Config: config},
    )
    setup_dishka(container=container, router=dp)

    async with container() as request_container:
        # Get TranslatorHub and admin notification
        hub = await request_container.get(TranslatorHub)

        # Register I18n middleware
        dp.message.middleware(UserAndLocaleMiddleware())
        dp.callback_query.middleware(UserAndLocaleMiddleware())

        await notify_admins_on_startup(bot, config, hub)

    await dp.start_polling(bot, config=config)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    with suppress(KeyboardInterrupt):
        asyncio.run(main())
