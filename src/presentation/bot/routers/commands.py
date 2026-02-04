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
from src.presentation.bot.utils.markups.settings import (
    get_onboarding_language_keyboard,
    get_welcome_keyboard,
)

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

    # New users: show onboarding language selection
    if user.is_new:
        # Use Telegram language for initial message, or English
        locale = extract_language_code(message.from_user.language_code)
        i18n = hub.get_translator_by_locale(locale)

        await message.answer(
            text=i18n.get("onboarding-language"),
            reply_markup=get_onboarding_language_keyboard(),
        )
        return

    # Returning users: show welcome with saved language (or Telegram language)
    if user.language_code:
        locale = user.language_code
    else:
        locale = extract_language_code(message.from_user.language_code)

    i18n = hub.get_translator_by_locale(locale)

    await message.answer(
        text=i18n.get("welcome", name=user.first_name),
        reply_markup=get_welcome_keyboard(i18n),
    )
