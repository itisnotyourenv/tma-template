from src.presentation.bot.utils.i18n import extract_language_code


class TestExtractLanguageCode:
    def test_returns_en_for_english(self) -> None:
        assert extract_language_code("en") == "en"

    def test_returns_ru_for_russian(self) -> None:
        assert extract_language_code("ru") == "ru"

    def test_handles_locale_with_region(self) -> None:
        assert extract_language_code("en-US") == "en"
        assert extract_language_code("ru-RU") == "ru"

    def test_passes_through_unsupported_language(self) -> None:
        # Fluentogram handles fallback to root_locale
        assert extract_language_code("de") == "de"
        assert extract_language_code("fr") == "fr"

    def test_returns_en_for_none(self) -> None:
        assert extract_language_code(None) == "en"

    def test_handles_uppercase(self) -> None:
        assert extract_language_code("EN") == "en"
        assert extract_language_code("RU") == "ru"
