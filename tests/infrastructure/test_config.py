import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest
import yaml
from pydantic import ValidationError

from src.infrastructure.config import PostgresConfig, AuthConfig, TelegramConfig, Config, load_config


class TestPostgresConfig:
    def test_valid_config(self):
        config = PostgresConfig(
            host="localhost",
            port=5432,
            user="test_user",
            password="test_pass",
            db="test_db"
        )
        
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.user == "test_user"
        assert config.password == "test_pass"
        assert config.db == "test_db"
        assert config.echo is False

    def test_echo_default_value(self):
        config = PostgresConfig(
            host="localhost",
            port=5432,
            user="user",
            password="pass",
            db="db"
        )
        
        assert config.echo is False

    def test_echo_explicit_value(self):
        config = PostgresConfig(
            host="localhost",
            port=5432,
            user="user",
            password="pass",
            db="db",
            echo=True
        )
        
        assert config.echo is True

    def test_url_property(self):
        config = PostgresConfig(
            host="localhost",
            port=5432,
            user="test_user",
            password="test_pass",
            db="test_db"
        )
        
        expected_url = "postgresql+asyncpg://test_user:test_pass@localhost:5432/test_db"
        assert config.url == expected_url

    def test_url_with_special_characters(self):
        config = PostgresConfig(
            host="db.example.com",
            port=5432,
            user="user@domain",
            password="pass@word!",
            db="test-db"
        )
        
        expected_url = "postgresql+asyncpg://user@domain:pass@word!@db.example.com:5432/test-db"
        assert config.url == expected_url

    def test_url_with_different_port(self):
        config = PostgresConfig(
            host="localhost",
            port=3306,
            user="user",
            password="pass",
            db="db"
        )
        
        expected_url = "postgresql+asyncpg://user:pass@localhost:3306/db"
        assert config.url == expected_url

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            PostgresConfig()

    def test_invalid_port_type(self):
        with pytest.raises(ValidationError):
            PostgresConfig(
                host="localhost",
                port="invalid_port",
                user="user",
                password="pass",
                db="db"
            )

    def test_invalid_echo_type(self):
        with pytest.raises(ValidationError):
            PostgresConfig(
                host="localhost",
                port=5432,
                user="user",
                password="pass",
                db="db",
                echo="invalid"
            )

    def test_negative_port(self):
        with pytest.raises(ValidationError):
            PostgresConfig(
                host="localhost",
                port=-1,
                user="user",
                password="pass",
                db="db"
            )

    def test_zero_port(self):
        config = PostgresConfig(
            host="localhost",
            port=0,
            user="user",
            password="pass",
            db="db"
        )
        assert config.port == 0

    def test_high_port_number(self):
        config = PostgresConfig(
            host="localhost",
            port=65535,
            user="user",
            password="pass",
            db="db"
        )
        assert config.port == 65535


class TestAuthConfig:
    def test_valid_config(self):
        config = AuthConfig(
            secret_key="test_secret_key",
            algorithm="HS256",
            access_token_expire_minutes=30
        )
        
        assert config.secret_key == "test_secret_key"
        assert config.algorithm == "HS256"
        assert config.access_token_expire_minutes == 30

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            AuthConfig()

    def test_invalid_expire_minutes_type(self):
        with pytest.raises(ValidationError):
            AuthConfig(
                secret_key="test_secret_key",
                algorithm="HS256",
                access_token_expire_minutes="invalid"
            )

    def test_negative_expire_minutes(self):
        config = AuthConfig(
            secret_key="test_secret_key",
            algorithm="HS256",
            access_token_expire_minutes=-1
        )
        assert config.access_token_expire_minutes == -1

    def test_zero_expire_minutes(self):
        config = AuthConfig(
            secret_key="test_secret_key",
            algorithm="HS256",
            access_token_expire_minutes=0
        )
        assert config.access_token_expire_minutes == 0


class TestTelegramConfig:
    def test_valid_config(self):
        config = TelegramConfig(
            bot_token="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
        )
        
        assert config.bot_token == "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            TelegramConfig()

    def test_empty_bot_token_allowed(self):
        config = TelegramConfig(bot_token="")
        assert config.bot_token == ""


class TestConfig:
    def test_valid_config(self):
        postgres_config = PostgresConfig(
            host="localhost",
            port=5432,
            user="user",
            password="pass",
            db="db"
        )
        auth_config = AuthConfig(
            secret_key="test_secret_key",
            algorithm="HS256",
            access_token_expire_minutes=30
        )
        telegram_config = TelegramConfig(
            bot_token="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
        )
        
        config = Config(postgres=postgres_config, auth=auth_config, telegram=telegram_config)
        assert config.postgres == postgres_config
        assert config.auth == auth_config
        assert config.telegram == telegram_config

    def test_missing_postgres_config(self):
        with pytest.raises(ValidationError):
            Config()

    def test_invalid_postgres_config(self):
        with pytest.raises(ValidationError):
            Config(postgres="invalid")


class TestLoadConfig:
    def test_load_valid_config_file(self):
        config_data = {
            "postgres": {
                "host": "localhost",
                "port": 5432,
                "user": "test_user",
                "password": "test_pass",
                "db": "test_db",
                "echo": True
            },
            "auth": {
                "secret_key": "test_secret_key",
                "algorithm": "HS256",
                "access_token_expire_minutes": 30
            },
            "telegram": {
                "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
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
                "db": "db"
            },
            "auth": {
                "secret_key": "test_secret_key",
                "algorithm": "HS256",
                "access_token_expire_minutes": 30
            },
            "telegram": {
                "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
            }
        }
        
        yaml_content = yaml.dump(config_data)
        
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("pathlib.Path.open", mock_open(read_data=yaml_content)):
                config = load_config()
                
                assert isinstance(config, Config)
                assert config.postgres.host == "localhost"
                assert config.auth.secret_key == "test_secret_key"
                assert config.telegram.bot_token == "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"

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
                "db": "db"
            }
        }
        
        yaml_content = yaml.dump(config_data)
        
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("pathlib.Path.open", mock_open(read_data=yaml_content)):
                with pytest.raises(ValidationError):
                    load_config("invalid_schema.yaml")

    def test_load_config_missing_required_fields(self):
        config_data = {
            "postgres": {
                "host": "localhost",
                "port": 5432
            }
        }
        
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
                "db": "db"
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
                "extra_field": "ignored"
            },
            "auth": {
                "secret_key": "test_secret_key",
                "algorithm": "HS256",
                "access_token_expire_minutes": 30
            },
            "telegram": {
                "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
            },
            "extra_config": "ignored"
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
                "echo": False
            },
            "auth": {
                "secret_key": "test_secret_key",
                "algorithm": "HS256",
                "access_token_expire_minutes": 30
            },
            "telegram": {
                "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
            }
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
                "db": "db"
            },
            "auth": {
                "secret_key": "test_secret_key",
                "algorithm": "HS256",
                "access_token_expire_minutes": 30
            },
            "telegram": {
                "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
            }
        }
        
        yaml_content = yaml.dump(config_data)
        
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("pathlib.Path.open", mock_open(read_data=yaml_content)):
                config = load_config()
                
                assert config.postgres.echo is False
