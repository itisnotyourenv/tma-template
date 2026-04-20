import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramAPIError
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from fluentogram import TranslatorHub

from src.infrastructure.config import Config
from src.infrastructure.i18n import DEFAULT_LANGUAGE, TranslatorRunner


async def _run_webhook(bot: Bot, dp: Dispatcher, config: Config) -> None:
    """Start an aiohttp server that receives Telegram updates via webhook."""
    webhook_config = config.telegram.webhook

    await bot.set_webhook(
        url=webhook_config.url,
        secret_token=webhook_config.secret_token,
        drop_pending_updates=webhook_config.drop_pending_updates,
        allowed_updates=dp.resolve_used_update_types(),
    )

    app = web.Application()
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=webhook_config.secret_token,
    ).register(app, path=webhook_config.path)
    setup_application(app, dp, bot=bot)

    async def _on_shutdown(_: web.Application) -> None:
        await bot.delete_webhook()

    app.on_shutdown.append(_on_shutdown)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=webhook_config.host, port=webhook_config.port)
    await site.start()
    logging.info(
        "Webhook server listening on %s:%s",
        webhook_config.host,
        webhook_config.port,
    )
    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()


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
