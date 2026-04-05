from unittest.mock import patch

from src.infrastructure.config import (
    AuthConfig,
    Config,
    PostgresConfig,
    SentryConfig,
    TelegramConfig,
)
from src.infrastructure.sentry import init_sentry


def _make_config(sentry: SentryConfig | None = None) -> Config:
    return Config(
        postgres=PostgresConfig(host="h", port=5432, user="u", password="p", db="d"),
        auth=AuthConfig(
            secret_key="s", algorithm="HS256", access_token_expire_minutes=30
        ),
        telegram=TelegramConfig(bot_token="t", admin_ids=[1], bot_username="b"),
        sentry=sentry,
    )


class TestInitSentry:
    def test_no_sentry_config_skips_init(self):
        config = _make_config(sentry=None)
        with patch("sentry_sdk.init") as mock_init:
            init_sentry(config)
            mock_init.assert_not_called()

    def test_sentry_config_calls_init(self):
        sentry_cfg = SentryConfig(
            dsn="https://key@sentry.io/123",
            environment="test",
            traces_sample_rate=0.5,
            profiles_sample_rate=0.25,
        )
        config = _make_config(sentry=sentry_cfg)
        with patch("sentry_sdk.init") as mock_init:
            init_sentry(config)
            mock_init.assert_called_once_with(
                dsn="https://key@sentry.io/123",
                environment="test",
                traces_sample_rate=0.5,
                profiles_sample_rate=0.25,
            )

    def test_sentry_config_default_values(self):
        sentry_cfg = SentryConfig(dsn="https://key@sentry.io/123")
        config = _make_config(sentry=sentry_cfg)
        with patch("sentry_sdk.init") as mock_init:
            init_sentry(config)
            mock_init.assert_called_once_with(
                dsn="https://key@sentry.io/123",
                environment="development",
                traces_sample_rate=1.0,
                profiles_sample_rate=1.0,
            )

    def test_sentry_init_failure_continues(self):
        sentry_cfg = SentryConfig(dsn="https://key@sentry.io/123")
        config = _make_config(sentry=sentry_cfg)
        with patch("sentry_sdk.init", side_effect=Exception("connection failed")):
            init_sentry(config)
