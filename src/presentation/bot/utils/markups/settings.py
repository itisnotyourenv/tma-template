from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.domain.user.vo import LanguageCode
from src.infrastructure.i18n import TranslatorRunner
from src.presentation.bot.utils.cb_data import (
    LanguageCBData,
    OnboardingCBData,
    SettingsCBData,
)


def get_welcome_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    """Create welcome/main menu keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.btn_settings(),
                    callback_data=SettingsCBData.menu,
                ),
            ],
        ]
    )


def get_settings_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    """Create settings menu keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.btn_language(),
                    callback_data=SettingsCBData.language,
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.btn_back(),
                    callback_data=SettingsCBData.back,
                ),
            ],
        ]
    )


def get_language_keyboard(
    i18n: TranslatorRunner, current: LanguageCode | None
) -> InlineKeyboardMarkup:
    """Create language selection keyboard with current language marked."""
    current_code = current.value if current else None

    def make_label(key: str, code: str) -> str:
        label = i18n.get(key)
        if current_code == code:
            return f"{label} ✓"
        return label

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=make_label("lang_en", "en"),
                    callback_data=LanguageCBData(code="en").pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text=make_label("lang_ru", "ru"),
                    callback_data=LanguageCBData(code="ru").pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.btn_back(),
                    callback_data=SettingsCBData.menu,
                ),
            ],
        ]
    )


def get_onboarding_language_keyboard() -> InlineKeyboardMarkup:
    """Create onboarding language selection keyboard (no localization needed)."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🇬🇧 English",
                    callback_data=OnboardingCBData(code="en").pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🇷🇺 Русский",
                    callback_data=OnboardingCBData(code="ru").pack(),
                ),
            ],
        ]
    )
