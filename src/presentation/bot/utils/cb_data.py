from aiogram.filters.callback_data import CallbackData


class SettingsCBData:
    menu: str = "settings:menu"
    language: str = "settings:language"
    back: str = "settings:back"


class LanguageCBData(CallbackData, prefix="lang"):
    code: str  # "en" or "ru"


class OnboardingCBData(CallbackData, prefix="onboard"):
    code: str  # "en" or "ru"
