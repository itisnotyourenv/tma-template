from pathlib import Path

import pytest
from dishka import make_async_container
from fluentogram import TranslatorHub

from src.infrastructure.i18n import I18nProvider


class TestI18nProvider:
    @pytest.fixture
    def locale_dir(self) -> Path:
        return Path(__file__).parent.parent.parent.parent.parent / "locales"

    async def test_provider_provides_translator_hub(self, locale_dir: Path) -> None:
        container = make_async_container(I18nProvider(locale_dir=locale_dir))

        async with container() as request_container:
            hub = await request_container.get(TranslatorHub)
            assert hub is not None
            assert isinstance(hub, TranslatorHub)

    async def test_provider_hub_is_singleton(self, locale_dir: Path) -> None:
        container = make_async_container(I18nProvider(locale_dir=locale_dir))

        async with container() as request_container:
            hub1 = await request_container.get(TranslatorHub)
            hub2 = await request_container.get(TranslatorHub)
            assert hub1 is hub2
