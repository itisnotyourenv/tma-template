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

    def test_extract_user_from_token_success(self, auth_service, valid_token):
        """Test successful extraction of user ID from valid token."""
        user_id = auth_service.extract_user_from_token(valid_token)
        assert user_id == 12345

    def test_extract_user_from_token_with_expired_token(self, auth_service, expired_token):
        """Test extraction from expired token still works (no validation)."""
        user_id = auth_service.extract_user_from_token(expired_token)
        assert user_id == 12345

    def test_extract_user_from_token_missing_subject(self, auth_service, mock_config):
        """Test extraction fails when token has no 'sub' claim."""
        payload = {
            "exp": datetime.now(UTC) + timedelta(minutes=30)
        }
        token_without_sub = encode(
            payload,
            mock_config.auth.secret_key,
            algorithm=mock_config.auth.algorithm
        )
        
        with pytest.raises(ValidationError, match="Token missing subject"):
            auth_service.extract_user_from_token(token_without_sub)

    def test_extract_user_from_token_invalid_user_id(self, auth_service, mock_config):
        """Test extraction fails when 'sub' claim is not a valid integer."""
        payload = {
            "sub": "not-a-number",
            "exp": datetime.now(UTC) + timedelta(minutes=30)
        }
        token_invalid_sub = encode(
            payload,
            mock_config.auth.secret_key,
            algorithm=mock_config.auth.algorithm
        )
        
        with pytest.raises(ValidationError, match="Cannot extract user from token"):
            auth_service.extract_user_from_token(token_invalid_sub)

    def test_extract_user_from_token_malformed_token(self, auth_service):
        """Test extraction fails with malformed JWT token."""
        malformed_token = "not.a.valid.jwt.token"
        
        with pytest.raises(ValidationError, match="Cannot extract user from token"):
            auth_service.extract_user_from_token(malformed_token)

    def test_extract_user_from_token_empty_token(self, auth_service):
        """Test extraction fails with empty token."""
        with pytest.raises(ValidationError, match="Cannot extract user from token"):
            auth_service.extract_user_from_token("")

    def test_extract_user_from_token_none_token(self, auth_service):
        """Test extraction fails with None token."""
        with pytest.raises(ValidationError, match="Cannot extract user from token"):
            auth_service.extract_user_from_token(None)

    @pytest.mark.parametrize("user_id", [1, 999, 123456789])
    def test_extract_user_from_token_various_user_ids(self, auth_service, mock_config, user_id):
        """Test extraction works with various valid user IDs."""
        payload = {
            "sub": str(user_id),
            "exp": datetime.now(UTC) + timedelta(minutes=30)
        }
        token = encode(
            payload,
            mock_config.auth.secret_key,
            algorithm=mock_config.auth.algorithm
        )
        
        extracted_user_id = auth_service.extract_user_from_token(token)
        assert extracted_user_id == user_id
