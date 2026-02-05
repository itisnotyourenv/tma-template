from aiogram import Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject
from fluentogram import TranslatorRunner

from src.application.referral.process import (
    ProcessReferralInputDTO,
    ProcessReferralInteractor,
)
from src.application.user.dtos import CreateUserOutputDTO
from src.presentation.bot.utils.markups.settings import (
    get_onboarding_language_keyboard,
    get_welcome_keyboard,
)

router = Router(name="commands")


async def _process_referral_if_applicable(
    user_id: int,
    command: CommandObject,
    process_referral: ProcessReferralInteractor,
) -> None:
    """Process referral code if present in command args."""
    if not command.args or not command.args.startswith("ref_"):
        return

    referral_code = command.args[4:]  # Remove "ref_" prefix
    await process_referral(
        ProcessReferralInputDTO(
            new_user_id=user_id,
            referral_code=referral_code,
        )
    )


async def _start_onboarding(
    message: Message,
    i18n: TranslatorRunner,
) -> None:
    """Start onboarding by asking user to select language."""
    await message.answer(
        text=i18n.get("onboarding-language"),
        reply_markup=get_onboarding_language_keyboard(),
    )


@router.message(CommandStart())
@inject
async def command_start_handler(
    message: Message,
    command: CommandObject,
    process_referral: FromDishka[ProcessReferralInteractor],
    i18n: TranslatorRunner,
    user: CreateUserOutputDTO,
) -> None:
    """Handle /start command."""
    if user.is_new:
        # Process referral for new users only
        await _process_referral_if_applicable(
            message.from_user.id, command, process_referral
        )
        # New users: show onboarding language selection
        await _start_onboarding(message, i18n)
        return

    await message.answer(
        text=i18n.get("welcome", name=user.first_name),
        reply_markup=get_welcome_keyboard(i18n),
    )
