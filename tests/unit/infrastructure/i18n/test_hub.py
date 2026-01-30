from pathlib import Path

from src.infrastructure.i18n.hub import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    create_translator_hub,
)


class TestTranslatorHub:
    def test_create_translator_hub_loads_languages(self) -> None:
        locales_dir = Path(__file__).parent.parent.parent.parent.parent / "locales"
        hub = create_translator_hub(locales_dir)

        # Should be able to get translators for all supported languages
        for lang in SUPPORTED_LANGUAGES:
            translator = hub.get_translator_by_locale(lang)
            assert translator is not None

    def test_default_language_is_english(self) -> None:
        assert DEFAULT_LANGUAGE == "en"

    def test_supported_languages_contains_en_and_ru(self) -> None:
        assert "en" in SUPPORTED_LANGUAGES
        assert "ru" in SUPPORTED_LANGUAGES

    def test_translator_returns_translated_string(self) -> None:
        locales_dir = Path(__file__).parent.parent.parent.parent.parent / "locales"
        hub = create_translator_hub(locales_dir)

        en_translator = hub.get_translator_by_locale("en")
        result = en_translator.get("welcome", name="Test")
        # fluent-compiler adds bidi isolation characters around variables
        assert result == "Hello, \u2068Test\u2069!"

    def test_russian_translator_returns_russian_string(self) -> None:
        locales_dir = Path(__file__).parent.parent.parent.parent.parent / "locales"
        hub = create_translator_hub(locales_dir)

        ru_translator = hub.get_translator_by_locale("ru")
        result = ru_translator.get("welcome", name="Тест")
        # fluent-compiler adds bidi isolation characters around variables
        assert result == "Привет, \u2068Тест\u2069!"  # noqa: RUF001
