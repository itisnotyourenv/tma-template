from src.presentation.bot.utils.i18n import get_user_locale


class TestGetUserLocale:
    def test_returns_en_for_english(self) -> None:
        assert get_user_locale("en") == "en"

    def test_returns_ru_for_russian(self) -> None:
        assert get_user_locale("ru") == "ru"

    def test_handles_locale_with_region(self) -> None:
        assert get_user_locale("en-US") == "en"
        assert get_user_locale("ru-RU") == "ru"

    def test_returns_default_for_unsupported_language(self) -> None:
        assert get_user_locale("de") == "en"
        assert get_user_locale("fr") == "en"

    def test_returns_default_for_none(self) -> None:
        assert get_user_locale(None) == "en"

    def test_handles_uppercase(self) -> None:
        assert get_user_locale("EN") == "en"
        assert get_user_locale("RU") == "ru"
