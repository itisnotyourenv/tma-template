from pathlib import Path

from pydantic import BaseModel, Field
import yaml


class PostgresConfig(BaseModel):
    host: str
    port: int = Field(gt=0, lt=65536)
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


class AuthConfig(BaseModel):
    secret_key: str = Field(min_length=32)
    algorithm: str
    access_token_expire_minutes: int


class TelegramConfig(BaseModel):
    bot_token: str
    admin_ids: list[int]
    bot_username: str
    tg_init_data: str | None = Field(
        default=None, description="Telegram init data for testing purposes"
    )


class Config(BaseModel):
    postgres: PostgresConfig
    auth: AuthConfig
    telegram: TelegramConfig


def load_config(file_name: str = "config.yaml") -> Config:
    with Path(file_name).open("r") as file:
        return Config.model_validate(yaml.safe_load(file))
