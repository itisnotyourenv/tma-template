from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject
from fluentogram import TranslatorHub

from src.presentation.bot.utils.i18n import extract_language_code

router = Router(name="admin")


@router.message(Command("example"))
@inject
async def example_admin_handler(
    message: Message,
    hub: FromDishka[TranslatorHub],
) -> None:
    """Handle /example admin command."""
    locale = extract_language_code(message.from_user.language_code)
    i18n = hub.get_translator_by_locale(locale)

    await message.answer(text=i18n.get("example-executed"))
