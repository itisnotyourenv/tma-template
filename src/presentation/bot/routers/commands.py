from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject
from fluentogram import TranslatorHub

from src.application.user.create import CreateUserInputDTO, CreateUserInteractor
from src.infrastructure.i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES

router = Router(name="commands")


def get_user_locale(language_code: str | None) -> str:
    """Get locale from Telegram language code."""
    if language_code:
        lang = language_code.split("-")[0].lower()
        if lang in SUPPORTED_LANGUAGES:
            return lang
    return DEFAULT_LANGUAGE


@router.message(CommandStart())
@inject
async def command_start_handler(
    message: Message,
    interactor: FromDishka[CreateUserInteractor],
    hub: FromDishka[TranslatorHub],
) -> None:
    """Handle /start command."""
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

    locale = get_user_locale(message.from_user.language_code)
    i18n = hub.get_translator_by_locale(locale)

    await message.answer(text=i18n.get("welcome", name=user.first_name))
