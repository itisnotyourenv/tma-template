"""i18n utilities for bot handlers."""

from src.infrastructure.i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES


def get_user_locale(language_code: str | None) -> str:
    """Get locale from Telegram language code.

    Args:
        language_code: Telegram user's language_code (e.g., "en", "ru", "en-US")

    Returns:
        Supported locale code, or DEFAULT_LANGUAGE if not supported.
    """
    if language_code:
        lang = language_code.split("-")[0].lower()
        if lang in SUPPORTED_LANGUAGES:
            return lang
    return DEFAULT_LANGUAGE
