from pathlib import Path

import yaml
from pydantic import BaseModel, field_validator


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


class TelegramConfig(BaseModel):
    bot_token: str
    admin_ids: list[int]
    bot_username: str
    tg_init_data: str = "for-auth-endpoint-tests"


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
