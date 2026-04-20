import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dishka import make_async_container
from dishka.integrations.aiogram import setup_dishka
from fluentogram import TranslatorHub

from src.infrastructure.config import Config, load_config
from src.infrastructure.di import (
    AuthProvider,
    DBProvider,
    I18nProvider,
    interactor_providers,
)
from src.infrastructure.sentry import init_sentry
from src.presentation.bot.middleware.user_and_locale import UserAndLocaleMiddleware
from src.presentation.bot.routers import setup_routers
from src.presentation.bot.utils.helpers import _run_webhook, notify_admins_on_startup


async def main() -> None:
    config = load_config()
    init_sentry(config)

    bot = Bot(
        token=config.telegram.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    interactor_provider_instances = [
        interactor() for interactor in interactor_providers
    ]

    dp = Dispatcher(config=config)
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

    if config.telegram.mode == "webhook":
        if config.telegram.webhook is None:
            # Defensive: the config validator already enforces this invariant,
            # so this branch should be unreachable. We keep the explicit check
            # because `assert` is stripped under `python -O`.
            raise RuntimeError(
                "telegram.webhook must be set when telegram.mode is 'webhook'"
            )
        await _run_webhook(bot, dp, config)
    else:
        await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
