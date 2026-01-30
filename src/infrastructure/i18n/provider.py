"""Dishka provider for internationalization."""

from pathlib import Path

from dishka import Provider, Scope, provide
from fluentogram import TranslatorHub

from .hub import create_translator_hub


class I18nProvider(Provider):
    """Dishka provider for internationalization.

    Provides TranslatorHub as an app-scoped singleton.
    """

    scope = Scope.APP

    def __init__(self, locale_dir: Path | None = None) -> None:
        """Initialize the i18n provider.

        Args:
            locale_dir: Path to locales directory. Defaults to project root /locales.
        """
        self.locale_dir = locale_dir
        super().__init__()

    @provide(scope=Scope.APP)
    def get_translator_hub(self) -> TranslatorHub:
        """Provide TranslatorHub as app-scoped singleton."""
        return create_translator_hub(self.locale_dir)
