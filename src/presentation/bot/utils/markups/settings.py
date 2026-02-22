from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.domain.user.vo import LanguageCode
from src.infrastructure.i18n.types import TranslatorRunner
from src.presentation.bot.utils.cb_data import (
    LanguageCBCode,
    LanguageCBData,
    OnboardingCBData,
    SettingsCBAction,
    SettingsCBData,
)


def get_welcome_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    """Create welcome/main menu keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("btn-settings"),
                    callback_data=SettingsCBData(action=SettingsCBAction.MENU).pack(),
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
                    text=i18n.get("btn-language"),
                    callback_data=SettingsCBData(
                        action=SettingsCBAction.LANGUAGE
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.get("btn-back"),
                    callback_data=SettingsCBData(action=SettingsCBAction.BACK).pack(),
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
                    text=make_label("lang-en", "en"),
                    callback_data=LanguageCBData(code=LanguageCBCode.EN).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text=make_label("lang-ru", "ru"),
                    callback_data=LanguageCBData(code=LanguageCBCode.RU).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.get("btn-back"),
                    callback_data=SettingsCBData(action=SettingsCBAction.MENU).pack(),
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
                    callback_data=OnboardingCBData(code=LanguageCBCode.EN).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🇷🇺 Русский",
                    callback_data=OnboardingCBData(code=LanguageCBCode.RU).pack(),
                ),
            ],
        ]
    )
