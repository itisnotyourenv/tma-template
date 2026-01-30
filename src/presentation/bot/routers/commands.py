from aiogram import Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject
from fluentogram import TranslatorHub

from src.application.referral.process import (
    ProcessReferralInputDTO,
    ProcessReferralInteractor,
)
from src.application.user.create import CreateUserInputDTO, CreateUserInteractor
from src.presentation.bot.utils.i18n import extract_language_code

router = Router(name="commands")


@router.message(CommandStart())
@inject
async def command_start_handler(
    message: Message,
    command: CommandObject,
    interactor: FromDishka[CreateUserInteractor],
    process_referral: FromDishka[ProcessReferralInteractor],
    hub: FromDishka[TranslatorHub],
) -> None:
    """Handle /start command."""
    user = await interactor(
        data=CreateUserInputDTO(
            id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
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

    locale = extract_language_code(message.from_user.language_code)
    i18n = hub.get_translator_by_locale(locale)

    await message.answer(text=i18n.get("welcome", name=user.first_name))
