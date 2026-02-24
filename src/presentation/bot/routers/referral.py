from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from src.application.referral.get_info import (
    GetReferralInfoInputDTO,
    GetReferralInfoInteractor,
)
from src.infrastructure.config import Config
from src.infrastructure.i18n import TranslatorRunner

router = Router(name="referral")


@router.message(Command("referral"))
@inject
async def referral_handler(
    message: Message,
    i18n: TranslatorRunner,
    get_referral_info: FromDishka[GetReferralInfoInteractor],
    config: FromDishka[Config],
) -> None:
    """Show user's referral link and statistics."""
    user_id = message.from_user.id
    info = await get_referral_info(GetReferralInfoInputDTO(user_id=user_id))

    if info is None:
        await message.answer(text=i18n.referral_user_not_found())
        return

    bot_username = config.telegram.bot_username
    referral_link = f"https://t.me/{bot_username}?start=ref_{info.referral_code}"

    text = i18n.referral_info(
        link=referral_link,
        count=info.referral_count,
    )

    await message.answer(text=text)
