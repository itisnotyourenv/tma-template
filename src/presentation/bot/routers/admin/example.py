from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject
from fluentogram import TranslatorHub

from src.infrastructure.i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES

router = Router(name="admin")


def get_user_locale(language_code: str | None) -> str:
    """Get locale from Telegram language code."""
    if language_code:
        lang = language_code.split("-")[0].lower()
        if lang in SUPPORTED_LANGUAGES:
            return lang
    return DEFAULT_LANGUAGE


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
