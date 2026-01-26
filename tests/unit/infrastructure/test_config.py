import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
import yaml
from pydantic import ValidationError

from src.infrastructure.config import (
    AuthConfig,
    Config,
    PostgresConfig,
    TelegramConfig,
    load_config,
)


class TestPostgresConfig:
    def test_valid_config(self):
        config = PostgresConfig(
            host="localhost",
            port=5432,
            user="test_user",
            password="test_pass",
            db="test_db",
        )

        assert config.host == "localhost"
        assert config.port == 5432
        assert config.user == "test_user"
        assert config.password == "test_pass"
        assert config.db == "test_db"
        assert config.echo is False

    def test_echo_default_value(self):
        config = PostgresConfig(
            host="localhost", port=5432, user="user", password="pass", db="db"
        )

        assert config.echo is False

    def test_echo_explicit_value(self):
        config = PostgresConfig(
            host="localhost",
            port=5432,
            user="user",
            password="pass",
            db="db",
            echo=True,
        )

        assert config.echo is True

    def test_url_property(self):
        config = PostgresConfig(
            host="localhost",
            port=5432,
            user="test_user",
            password="test_pass",
            db="test_db",
        )

        expected_url = "postgresql+asyncpg://test_user:test_pass@localhost:5432/test_db"
        assert config.url == expected_url

    @pytest.mark.parametrize(
        "host,port,user,password,db,expected_url",
        [
            (
                "localhost",
                5432,
                "test_user",
                "test_pass",
                "test_db",
                "postgresql+asyncpg://test_user:test_pass@localhost:5432/test_db",
            ),
            (
                "db.example.com",
                5432,
                "user@domain",
                "pass@word!",
                "test-db",
                "postgresql+asyncpg://user@domain:pass@word!@db.example.com:5432/test-db",
            ),
            (
                "localhost",
                3306,
                "user",
                "pass",
                "db",
                "postgresql+asyncpg://user:pass@localhost:3306/db",
            ),
        ],
    )
    def test_url_property_variations(
        self, host, port, user, password, db, expected_url
    ):
        config = PostgresConfig(
            host=host, port=port, user=user, password=password, db=db
        )
        assert config.url == expected_url

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            PostgresConfig()

    @pytest.mark.parametrize(
        "port,echo,should_raise",
        [
            ("invalid_port", False, True),  # Invalid port type
            (5432, "invalid", True),  # Invalid echo type
            (-1, False, True),  # Negative port
            (65536, False, False),  # High port (valid)
            (5432, True, False),  # Valid config
            (3306, False, False),  # Valid different port
        ],
    )
    def test_port_and_echo_validation(self, port, echo, should_raise):
        if should_raise:
            with pytest.raises(ValidationError):
                PostgresConfig(
                    host="localhost",
                    port=port,
                    user="user",
                    password="pass",
                    db="db",
                    echo=echo,
                )
        else:
            config = PostgresConfig(
                host="localhost",
                port=port,
                user="user",
                password="pass",
                db="db",
                echo=echo,
            )
            assert config.port == port
            assert config.echo == echo

    @pytest.mark.parametrize(
        "port,expected",
        [
            (0, 0),
            (5432, 5432),
            (65535, 65535),
            (1, 1),
            (8080, 8080),
        ],
    )
    def test_valid_ports(self, port, expected):
        config = PostgresConfig(
            host="localhost", port=port, user="user", password="pass", db="db"
        )
        assert config.port == expected


class TestAuthConfig:
    def test_valid_config(self):
        config = AuthConfig(
            secret_key="test_secret_key",
            algorithm="HS256",
            access_token_expire_minutes=30,
        )

        assert config.secret_key == "test_secret_key"
        assert config.algorithm == "HS256"
        assert config.access_token_expire_minutes == 30

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            AuthConfig()

    @pytest.mark.parametrize(
        "expire_minutes,should_raise,expected",
        [
            ("invalid", True, None),  # Invalid type
            (30, False, 30),  # Valid positive
            (-1, False, -1),  # Negative (allowed)
            (0, False, 0),  # Zero (allowed)
            (60, False, 60),  # Different valid value
        ],
    )
    def test_expire_minutes_validation(self, expire_minutes, should_raise, expected):
        if should_raise:
            with pytest.raises(ValidationError):
                AuthConfig(
                    secret_key="test_secret_key",
                    algorithm="HS256",
                    access_token_expire_minutes=expire_minutes,
                )
        else:
            config = AuthConfig(
                secret_key="test_secret_key",
                algorithm="HS256",
                access_token_expire_minutes=expire_minutes,
            )
            assert config.access_token_expire_minutes == expected


class TestTelegramConfig:
    def test_valid_config(self):
        config = TelegramConfig(
            bot_token="123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
            admin_ids=[123456789],
        )

        assert config.bot_token == "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
        assert config.admin_ids == [123456789]

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            TelegramConfig()

    @pytest.mark.parametrize(
        "bot_token,expected",
        [
            (
                "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
                "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
            ),
            ("", ""),
            ("test_token", "test_token"),
        ],
    )
    def test_bot_token_values(self, bot_token, expected):
        config = TelegramConfig(bot_token=bot_token, admin_ids=[123456789])
        assert config.bot_token == expected


class TestConfig:
    def test_valid_config(self):
        postgres_config = PostgresConfig(
            host="localhost", port=5432, user="user", password="pass", db="db"
        )
        auth_config = AuthConfig(
            secret_key="test_secret_key",
            algorithm="HS256",
            access_token_expire_minutes=30,
        )
        telegram_config = TelegramConfig(
            bot_token="123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
            admin_ids=[123456789],
        )

        config = Config(
            postgres=postgres_config, auth=auth_config, telegram=telegram_config
        )
        assert config.postgres == postgres_config
        assert config.auth == auth_config
        assert config.telegram == telegram_config

    @pytest.mark.parametrize(
        "postgres,should_raise",
        [
            (None, True),  # Missing postgres config
            ("invalid", True),  # Invalid postgres config
        ],
    )
    def test_config_validation(self, postgres, should_raise):
        if should_raise:
            with pytest.raises(ValidationError):
                Config(postgres=postgres)


class TestLoadConfig:
    def test_load_valid_config_file(self):
        config_data = {
            "postgres": {
                "host": "localhost",
                "port": 5432,
                "user": "test_user",
                "password": "test_pass",
                "db": "test_db",
                "echo": True,
            },
            "auth": {
                "secret_key": "test_secret_key",
                "algorithm": "HS256",
                "access_token_expire_minutes": 30,
            },
            "telegram": {
                "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
                "admin_ids": [123456789],
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            temp_file = f.name

        try:
            config = load_config(temp_file)

            assert isinstance(config, Config)
            assert config.postgres.host == "localhost"
            assert config.postgres.port == 5432
            assert config.postgres.user == "test_user"
            assert config.postgres.password == "test_pass"
            assert config.postgres.db == "test_db"
            assert config.postgres.echo is True
            assert config.auth.secret_key == "test_secret_key"
            assert config.auth.algorithm == "HS256"
            assert config.auth.access_token_expire_minutes == 30
            assert config.telegram.bot_token == "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
        finally:
            Path(temp_file).unlink()

    def test_load_config_with_default_filename(self):
        config_data = {
            "postgres": {
                "host": "localhost",
                "port": 5432,
                "user": "user",
                "password": "pass",
                "db": "db",
            },
            "auth": {
                "secret_key": "test_secret_key",
                "algorithm": "HS256",
                "access_token_expire_minutes": 30,
            },
            "telegram": {
                "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
                "admin_ids": [123456789],
            },
        }

        yaml_content = yaml.dump(config_data)

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("pathlib.Path.open", mock_open(read_data=yaml_content)):
                config = load_config()

                assert isinstance(config, Config)
                assert config.postgres.host == "localhost"
                assert config.auth.secret_key == "test_secret_key"
                assert (
                    config.telegram.bot_token == "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
                )

    def test_load_config_missing_file(self):
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent_file.yaml")

    def test_load_config_invalid_yaml(self):
        invalid_yaml = "invalid: yaml: content: ["

        with patch("builtins.open", mock_open(read_data=invalid_yaml)):
            with patch("pathlib.Path.open", mock_open(read_data=invalid_yaml)):
                with pytest.raises(yaml.YAMLError):
                    load_config("invalid.yaml")

    def test_load_config_invalid_schema(self):
        config_data = {
            "postgres": {
                "host": "localhost",
                "port": "invalid_port",
                "user": "user",
                "password": "pass",
                "db": "db",
            }
        }

        yaml_content = yaml.dump(config_data)

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("pathlib.Path.open", mock_open(read_data=yaml_content)):
                with pytest.raises(ValidationError):
                    load_config("invalid_schema.yaml")

    def test_load_config_missing_required_fields(self):
        config_data = {"postgres": {"host": "localhost", "port": 5432}}

        yaml_content = yaml.dump(config_data)

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("pathlib.Path.open", mock_open(read_data=yaml_content)):
                with pytest.raises(ValidationError):
                    load_config("missing_fields.yaml")

    def test_load_config_empty_file(self):
        with patch("builtins.open", mock_open(read_data="")):
            with patch("pathlib.Path.open", mock_open(read_data="")):
                with pytest.raises(ValidationError):
                    load_config("empty.yaml")

    def test_load_config_null_values(self):
        config_data = {
            "postgres": {
                "host": None,
                "port": 5432,
                "user": "user",
                "password": "pass",
                "db": "db",
            }
        }

        yaml_content = yaml.dump(config_data)

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("pathlib.Path.open", mock_open(read_data=yaml_content)):
                with pytest.raises(ValidationError):
                    load_config("null_values.yaml")

    def test_load_config_extra_fields_ignored(self):
        config_data = {
            "postgres": {
                "host": "localhost",
                "port": 5432,
                "user": "user",
                "password": "pass",
                "db": "db",
                "extra_field": "ignored",
            },
            "auth": {
                "secret_key": "test_secret_key",
                "algorithm": "HS256",
                "access_token_expire_minutes": 30,
            },
            "telegram": {
                "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
                "admin_ids": [123456789],
            },
            "extra_config": "ignored",
        }

        yaml_content = yaml.dump(config_data)

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("pathlib.Path.open", mock_open(read_data=yaml_content)):
                config = load_config("extra_fields.yaml")

                assert isinstance(config, Config)
                assert config.postgres.host == "localhost"
                assert not hasattr(config.postgres, "extra_field")
                assert not hasattr(config, "extra_config")

    def test_load_config_with_echo_false(self):
        config_data = {
            "postgres": {
                "host": "localhost",
                "port": 5432,
                "user": "user",
                "password": "pass",
                "db": "db",
                "echo": False,
            },
            "auth": {
                "secret_key": "test_secret_key",
                "algorithm": "HS256",
                "access_token_expire_minutes": 30,
            },
            "telegram": {
                "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
                "admin_ids": [123456789],
            },
        }

        yaml_content = yaml.dump(config_data)

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("pathlib.Path.open", mock_open(read_data=yaml_content)):
                config = load_config()

                assert config.postgres.echo is False

    def test_load_config_without_echo_uses_default(self):
        config_data = {
            "postgres": {
                "host": "localhost",
                "port": 5432,
                "user": "user",
                "password": "pass",
                "db": "db",
            },
            "auth": {
                "secret_key": "test_secret_key",
                "algorithm": "HS256",
                "access_token_expire_minutes": 30,
            },
            "telegram": {
                "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
                "admin_ids": [123456789],
            },
        }

        yaml_content = yaml.dump(config_data)

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("pathlib.Path.open", mock_open(read_data=yaml_content)):
                config = load_config()

                assert config.postgres.echo is False
