from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject
from fluentogram import TranslatorHub

from src.application.referral.get_info import (
    GetReferralInfoInputDTO,
    GetReferralInfoInteractor,
)
from src.infrastructure.config import Config
from src.presentation.bot.utils.i18n import extract_language_code

router = Router(name="referral")


@router.message(Command("referral"))
@inject
async def referral_handler(
    message: Message,
    hub: FromDishka[TranslatorHub],
    get_referral_info: FromDishka[GetReferralInfoInteractor],
    config: FromDishka[Config],
) -> None:
    """Show user's referral link and statistics."""
    locale = extract_language_code(message.from_user.language_code)
    i18n = hub.get_translator_by_locale(locale)

    user_id = message.from_user.id
    info = await get_referral_info(GetReferralInfoInputDTO(user_id=user_id))

    if info is None:
        await message.answer(text=i18n.get("referral-user-not-found"))
        return

    bot_username = config.telegram.bot_username
    referral_link = f"https://t.me/{bot_username}?start=ref_{info.referral_code}"

    text = i18n.get(
        "referral-info",
        link=referral_link,
        count=info.referral_count,
    )

    await message.answer(text=text)
