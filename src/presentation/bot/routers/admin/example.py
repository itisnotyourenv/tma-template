from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject
from fluentogram import TranslatorHub

from src.presentation.bot.utils.i18n import get_user_locale

router = Router(name="admin")


@router.message(Command("example"))
@inject
async def example_admin_handler(
    message: Message,
    hub: FromDishka[TranslatorHub],
) -> None:
    """Handle /example admin command."""
    locale = get_user_locale(message.from_user.language_code)
    i18n = hub.get_translator_by_locale(locale)

    await message.answer(text=i18n.get("example-executed"))
