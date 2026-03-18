import os

import pytest

from src.infrastructure.config import Config, load_config


@pytest.fixture(scope="session")
def test_config() -> Config:
    config = load_config("config-test.yaml")

    if os.environ.get("CI_POSTGRES_HOST"):
        config.postgres.host = os.environ["CI_POSTGRES_HOST"]
    if os.environ.get("CI_POSTGRES_PORT"):
        config.postgres.port = int(os.environ["CI_POSTGRES_PORT"])

    return config


pytest_plugins = [
    "tests.utils.model_factories.user",
]
