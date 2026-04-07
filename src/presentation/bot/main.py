import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dishka import make_async_container
from dishka.integrations.aiogram import setup_dishka
from fluentogram import TranslatorHub

from src.infrastructure.config import Config, WebhookConfig, load_config
from src.infrastructure.di import (
    AuthProvider,
    DBProvider,
    I18nProvider,
    interactor_providers,
)
from src.infrastructure.i18n import DEFAULT_LANGUAGE, TranslatorRunner
from src.infrastructure.sentry import init_sentry
from src.presentation.bot.middleware.user_and_locale import UserAndLocaleMiddleware
from src.presentation.bot.routers import setup_routers


async def notify_admins_on_startup(
    bot: Bot, config: Config, hub: TranslatorHub
) -> None:
    """Send notification to admins when bot starts up."""
    i18n: TranslatorRunner = hub.get_translator_by_locale(DEFAULT_LANGUAGE)
    for admin_id in config.telegram.admin_ids:
        try:
            await bot.send_message(chat_id=admin_id, text=i18n.bot_started())
        except TelegramAPIError as e:
            logging.warning("Failed to notify admin %s: %s", admin_id, e)


async def _run_webhook(bot: Bot, dp: Dispatcher, webhook: WebhookConfig) -> None:
    """Start an aiohttp server that receives Telegram updates via webhook."""
    await bot.set_webhook(
        url=webhook.url,
        secret_token=webhook.secret_token,
        drop_pending_updates=webhook.drop_pending_updates,
        allowed_updates=dp.resolve_used_update_types(),
    )

    app = web.Application()
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=webhook.secret_token,
    ).register(app, path=webhook.path)
    setup_application(app, dp, bot=bot)

    async def _on_shutdown(_: web.Application) -> None:
        await bot.delete_webhook()

    app.on_shutdown.append(_on_shutdown)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=webhook.host, port=webhook.port)
    await site.start()
    logging.info("Webhook server listening on %s:%s", webhook.host, webhook.port)
    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()


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
        assert config.telegram.webhook is not None  # guaranteed by config validator
        await _run_webhook(bot, dp, config.telegram.webhook)
    else:
        await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
