import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka, inject
from fluentogram import TranslatorHub, TranslatorRunner

from src.application.user.interactors.update_language import (
    UpdateLanguageDTO,
    UpdateLanguageInteractor,
)
from src.domain.user import UserRepository
from src.domain.user.vo import LanguageCode, UserId
from src.presentation.bot.utils import edit_or_answer
from src.presentation.bot.utils.cb_data import LanguageCBData, SettingsCBData
from src.presentation.bot.utils.markups.settings import (
    get_language_keyboard,
    get_settings_keyboard,
    get_welcome_keyboard,
)

logger = logging.getLogger(__name__)

router = Router(name="settings")


@router.callback_query(F.data == SettingsCBData.menu)
@inject
async def settings_menu(
    callback: CallbackQuery,
    i18n: TranslatorRunner,
) -> None:
    """Handle Settings button from main menu."""
    logger.info("User %s opened settings menu", callback.from_user.id)
    await edit_or_answer(
        update=callback,
        text=i18n.get("settings-title"),
        reply_markup=get_settings_keyboard(i18n),
    )
    await callback.answer()


@router.callback_query(F.data == SettingsCBData.language)
@inject
async def language_menu(
    callback: CallbackQuery,
    i18n: TranslatorRunner,
    user_repository: FromDishka[UserRepository],
) -> None:
    """Handle Language button in settings."""
    logger.info("User %s opened language menu", callback.from_user.id)
    user_id = UserId(callback.from_user.id)
    user = await user_repository.get_user(user_id)
    current_language = user.language_code if user else None

    await edit_or_answer(
        update=callback,
        text=i18n.get("settings-language-title"),
        reply_markup=get_language_keyboard(i18n, current_language),
    )
    await callback.answer()


@router.callback_query(LanguageCBData.filter())
@inject
async def change_language(
    callback: CallbackQuery,
    callback_data: LanguageCBData,
    interactor: FromDishka[UpdateLanguageInteractor],
    hub: FromDishka[TranslatorHub],
) -> None:
    """Handle language selection from settings."""
    user_id = UserId(callback.from_user.id)
    new_language = LanguageCode(callback_data.code)
    logger.info(
        "User %s changing language to %s", callback.from_user.id, new_language.value
    )

    await interactor(
        UpdateLanguageDTO(
            user_id=user_id,
            language_code=new_language,
        )
    )

    # Get translator for new language and redraw
    i18n = hub.get_translator_by_locale(new_language.value)

    await edit_or_answer(
        update=callback,
        text=i18n.get("settings-language-changed"),
        reply_markup=get_settings_keyboard(i18n),
    )
    await callback.answer()


@router.callback_query(F.data == SettingsCBData.back)
@inject
async def back_to_main_menu(
    callback: CallbackQuery,
    i18n: TranslatorRunner,
    user_repository: FromDishka[UserRepository],
) -> None:
    """Handle Back button to return to main menu."""
    logger.info("User %s returned to main menu from settings", callback.from_user.id)
    user_id = UserId(callback.from_user.id)
    user = await user_repository.get_user(user_id)

    await edit_or_answer(
        update=callback,
        text=i18n.get("welcome", name=user.first_name.value if user else "User"),
        reply_markup=get_welcome_keyboard(i18n),
    )
    await callback.answer()
