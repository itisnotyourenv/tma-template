from aiogram import Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from src.application.referral.process import (
    ProcessReferralInputDTO,
    ProcessReferralInteractor,
)
from src.application.user.create import CreateUserInputDTO, CreateUserInteractor

router = Router(name="commands")


@router.message(CommandStart())
@inject
async def command_start_handler(
    message: Message,
    command: CommandObject,
    interactor: FromDishka[CreateUserInteractor],
    process_referral: FromDishka[ProcessReferralInteractor],
) -> None:
    """This handler receives messages with `/start` command"""
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

    # Process referral for new users only
    if user.is_new and command.args and command.args.startswith("ref_"):
        referral_code = command.args[4:]  # Remove "ref_" prefix
        await process_referral(
            ProcessReferralInputDTO(
                new_user_id=message.from_user.id,
                referral_code=referral_code,
            )
        )

    msg = f"Hello, {user.first_name}!"
    await message.answer(text=msg)
