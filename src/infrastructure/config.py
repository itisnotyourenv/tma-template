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

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    @field_validator("port")  # noqa
    @classmethod
    def port_validator(cls, v):
        if v < 0:
            raise ValueError("Port must be between 1 and 65535")
        return v


class AuthConfig(BaseModel):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int


class TelegramConfig(BaseModel):
    bot_token: str
    tg_init_data: str = "for-auth-endpoint-tests"


class Config(BaseModel):
    postgres: PostgresConfig
    auth: AuthConfig
    telegram: TelegramConfig


def load_config(file_name: str = "config.yaml") -> Config:
    with Path(file_name).open("r") as f:
        return Config.model_validate(yaml.safe_load(f))
