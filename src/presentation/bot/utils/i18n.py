"""i18n utilities for bot handlers."""


def extract_language_code(language_code: str | None) -> str:
    """Extract base language code from Telegram language_code.

    Args:
        language_code: Telegram user's language_code (e.g., "en", "ru", "en-US")

    Returns:
        Base language code (e.g., "en" from "en-US"), or "en" if None.
        Fluentogram handles fallback to root_locale for unsupported languages.
    """
    if language_code:
        return language_code.split("-")[0].lower()
    return "en"
