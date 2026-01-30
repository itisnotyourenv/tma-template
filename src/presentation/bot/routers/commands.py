from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject
from fluentogram import TranslatorHub

from src.application.user.create import CreateUserInputDTO, CreateUserInteractor
from src.presentation.bot.utils.i18n import get_user_locale

router = Router(name="commands")


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
