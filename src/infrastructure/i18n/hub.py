"""TranslatorHub factory and utilities for i18n."""

from pathlib import Path

from fluent_compiler.bundle import FluentBundle
from fluentogram import FluentTranslator, TranslatorHub

SUPPORTED_LANGUAGES = ("en", "ru")
DEFAULT_LANGUAGE = "en"


def load_ftl_files(locale_dir: Path, language: str) -> str:
    """Load and concatenate all .ftl files for a language."""
    lang_dir = locale_dir / language
    if not lang_dir.exists():
        return ""

    ftl_content = []
    for ftl_file in sorted(lang_dir.glob("*.ftl")):
        ftl_content.append(ftl_file.read_text(encoding="utf-8"))

    return "\n\n".join(ftl_content)


def create_translator_hub(locale_dir: Path | None = None) -> TranslatorHub:
    """Create and configure the TranslatorHub with all supported languages.

    Args:
        locale_dir: Path to locales directory. Defaults to project root /locales.

    Returns:
        Configured TranslatorHub instance.
    """
    if locale_dir is None:
        locale_dir = Path(__file__).parent.parent.parent.parent / "locales"

    translators = []

    for lang in SUPPORTED_LANGUAGES:
        ftl_content = load_ftl_files(locale_dir, lang)
        if ftl_content:
            bundle = FluentBundle.from_string(lang, ftl_content)
            translators.append(FluentTranslator(lang, translator=bundle))

    # Configure locale mapping with English as fallback
    locale_map = {
        "en": ("en",),
        "ru": ("ru", "en"),
    }

    return TranslatorHub(locale_map, translators, root_locale="en")
