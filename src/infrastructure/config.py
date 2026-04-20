import re
from pathlib import Path
from typing import ClassVar, Literal

import yaml
from pydantic import BaseModel, field_validator, model_validator


class PostgresConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str
    db: str
    echo: bool = False
    pool_size: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    max_overflow: int = 20
    pool_pre_ping: bool = True
    echo_pool: bool = False

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    @field_validator("port")
    @classmethod
    def port_validator(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Port must be between 1 and 65535")
        return v


class AuthConfig(BaseModel):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int


class WebhookConfig(BaseModel):
    _SECRET_TOKEN_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^[A-Za-z0-9_-]{1,256}$"
    )

    url: str
    path: str = "/webhook"
    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8081
    secret_token: str | None = None
    drop_pending_updates: bool = False

    @field_validator("url")
    @classmethod
    def url_validator(cls, v: str) -> str:
        if not v.startswith("https://"):
            raise ValueError("Webhook URL must use https:// (required by Telegram)")
        return v

    @field_validator("path")
    @classmethod
    def path_validator(cls, v: str) -> str:
        if not v.startswith("/"):
            raise ValueError("Webhook path must start with '/'")
        return v

    @field_validator("port")
    @classmethod
    def port_validator(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v

    @field_validator("secret_token")
    @classmethod
    def secret_token_validator(cls, v: str | None) -> str | None:
        if v is not None and not cls._SECRET_TOKEN_PATTERN.match(v):
            raise ValueError(
                "secret_token must match [A-Za-z0-9_-]{1,256} (Telegram requirement)"
            )
        return v


class TelegramConfig(BaseModel):
    bot_token: str
    admin_ids: list[int]
    bot_username: str
    tg_init_data: str = "for-auth-endpoint-tests"
    mode: Literal["polling", "webhook"] = "polling"
    webhook: WebhookConfig | None = None

    @model_validator(mode="after")
    def _webhook_required_in_webhook_mode(self) -> "TelegramConfig":
        if self.mode == "webhook" and self.webhook is None:
            raise ValueError(
                "telegram.webhook config must be set when telegram.mode is 'webhook'"
            )
        return self


class SentryConfig(BaseModel):
    dsn: str
    environment: str = "development"  # development, production
    traces_sample_rate: float = 1.0
    profiles_sample_rate: float = 1.0

    @field_validator("traces_sample_rate", "profiles_sample_rate")
    @classmethod
    def validate_sample_rate(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("Sample rate must be between 0.0 and 1.0")
        return v


class Config(BaseModel):
    postgres: PostgresConfig
    auth: AuthConfig
    telegram: TelegramConfig
    sentry: SentryConfig | None = None


def load_config(file_name: str = "config.yaml") -> Config:
    with Path(file_name).open("r") as f:
        return Config.model_validate(yaml.safe_load(f))
