from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from src.application.referral.get_info import GetReferralInfoInteractor
from src.infrastructure.config import Config

router = Router(name="referral")


@router.message(Command("referral"))
@inject
async def referral_handler(
    message: Message,
    get_referral_info: FromDishka[GetReferralInfoInteractor],
    config: FromDishka[Config],
) -> None:
    """Show user's referral link and statistics."""
    user_id = message.from_user.id
    info = await get_referral_info(user_id)

    bot_username = config.telegram.bot_username
    referral_link = f"https://t.me/{bot_username}?start=ref_{info.referral_code}"

    text = (
        f"Your referral link:\n{referral_link}\n\nInvited users: {info.referral_count}"
    )

    await message.answer(text=text)
