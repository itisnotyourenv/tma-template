import pytest
from unittest.mock import Mock
from jose.jwt import encode
from datetime import datetime, UTC, timedelta

from src.application.common.exceptions import ValidationError
from src.infrastructure.auth import AuthServiceImpl
from src.infrastructure.config import Config


class TestAuthServiceImpl:
    
    @pytest.fixture
    def mock_config(self):
        config = Mock(spec=Config)
        auth_config = Mock()
        auth_config.secret_key = "test-secret-key"
        auth_config.algorithm = "HS256"
        auth_config.access_token_expire_minutes = 30
        config.auth = auth_config
        return config
    
    @pytest.fixture
    def auth_service(self, mock_config):
        return AuthServiceImpl(mock_config)
    
    @pytest.fixture
    def valid_token(self, mock_config):
        """Create a valid JWT token for testing."""
        payload = {
            "sub": "12345",
            "exp": datetime.now(UTC) + timedelta(minutes=30)
        }
        return encode(
            payload,
            mock_config.auth.secret_key,
            algorithm=mock_config.auth.algorithm
        )
    
    @pytest.fixture
    def expired_token(self, mock_config):
        """Create an expired JWT token for testing."""
        payload = {
            "sub": "12345",
            "exp": datetime.now(UTC) - timedelta(minutes=30)
        }
        return encode(
            payload,
            mock_config.auth.secret_key,
            algorithm=mock_config.auth.algorithm
        )
