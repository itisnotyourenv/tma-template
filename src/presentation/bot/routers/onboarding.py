from aiogram import Router
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka, inject
from fluentogram import TranslatorHub

from src.application.user.interactors.update_language import (
    UpdateLanguageDTO,
    UpdateLanguageInteractor,
)
from src.domain.user import UserRepository
from src.domain.user.vo import LanguageCode, UserId
from src.presentation.bot.utils import edit_or_answer
from src.presentation.bot.utils.cb_data import OnboardingCBData
from src.presentation.bot.utils.markups.settings import get_welcome_keyboard

router = Router(name="onboarding")


@router.callback_query(OnboardingCBData.filter())
@inject
async def onboarding_language_selected(
    callback: CallbackQuery,
    callback_data: OnboardingCBData,
    interactor: FromDishka[UpdateLanguageInteractor],
    user_repository: FromDishka[UserRepository],
    hub: FromDishka[TranslatorHub],
) -> None:
    """Handle language selection during onboarding."""
    await callback.answer()

    user_id = UserId(callback.from_user.id)
    new_language = LanguageCode(callback_data.code)

    # Save language preference
    await interactor(
        UpdateLanguageDTO(
            user_id=user_id,
            language_code=new_language,
        )
    )

    # Get user and translator for new language
    user = await user_repository.get_user(user_id)
    i18n = hub.get_translator_by_locale(new_language.value)

    # Show welcome message in chosen language
    await edit_or_answer(
        callback,
        text=i18n.get("welcome", name=user.first_name.value if user else "User"),
        reply_markup=get_welcome_keyboard(i18n),
    )
