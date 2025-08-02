import pytest

from src.infrastructure.config import Config, load_config


@pytest.fixture(scope="session")
def test_config() -> Config:
    config = load_config("config-test.yaml")
    return config



pytest_plugins = [
    "tests.utils.model_factories.user",
]
