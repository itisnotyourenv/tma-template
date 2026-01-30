"""Internationalization (i18n) infrastructure module."""

from .hub import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    create_translator_hub,
)

__all__ = [
    "DEFAULT_LANGUAGE",
    "SUPPORTED_LANGUAGES",
    "create_translator_hub",
]
