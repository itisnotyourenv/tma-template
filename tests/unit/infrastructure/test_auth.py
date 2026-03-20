from datetime import UTC, datetime
from unittest.mock import Mock, patch

from litestar.security.jwt import Token
import pytest

from src.application.auth.exceptions import InvalidInitDataError
from src.application.common.exceptions import ValidationError
from src.application.interfaces.auth import InitDataDTO
from src.infrastructure.auth import AuthServiceImpl
from src.infrastructure.config import Config


class TestAuthServiceImpl:
    @pytest.fixture
    def mock_config(self):
        config = Mock(spec=Config)
        auth_config = Mock()
        auth_config.secret_key = "3d1b2a2127de6f65804364813b3107b2"
        auth_config.algorithm = "HS256"
        auth_config.access_token_expire_minutes = 30
        config.auth = auth_config

        telegram_config = Mock()
        telegram_config.bot_token = "test-bot-token"
        config.telegram = telegram_config

        return config

    @pytest.fixture
    def auth_service(self, mock_config):
        return AuthServiceImpl(mock_config)

    @pytest.fixture
    def valid_init_data_mock(self):
        """Mock valid parsed init data."""
        user_mock = Mock()
        user_mock.id = 12345
        user_mock.username = "testuser"
        user_mock.first_name = "Test"
        user_mock.last_name = "User"
        user_mock.language_code = "en"

        parsed_data_mock = Mock()
        parsed_data_mock.user = user_mock
        parsed_data_mock.start_param = "start123"

        return parsed_data_mock

    def test_create_access_token_success(self, auth_service, mock_config):
        user_id = 12345

        token = auth_service.create_access_token(user_id)

        assert isinstance(token, str)
        assert len(token) > 0

        decoded = Token.decode(
            encoded_token=token,
            secret=mock_config.auth.secret_key,
            algorithm=mock_config.auth.algorithm,
        )
        assert decoded.sub == str(user_id)
        assert decoded.exp > datetime.now(UTC)

    @patch("src.infrastructure.auth.safe_parse_webapp_init_data")
    def test_validate_init_data_success(
        self, mock_parse, auth_service, valid_init_data_mock
    ):
        mock_parse.return_value = valid_init_data_mock
        init_data = "valid_init_data_string"

        result = auth_service.validate_init_data(init_data)

        assert isinstance(result, InitDataDTO)
        assert result.user_id == 12345
        assert result.username == "testuser"
        assert result.first_name == "Test"
        assert result.last_name == "User"
        assert result.start_param == "start123"
        assert result.ui_language_code == "en"

        mock_parse.assert_called_once_with("test-bot-token", init_data)

    @patch("src.infrastructure.auth.safe_parse_webapp_init_data")
    def test_validate_init_data_success_with_optional_none(
        self, mock_parse, auth_service
    ):
        user_mock = Mock()
        user_mock.id = 67890
        user_mock.username = None
        user_mock.first_name = "Test"
        user_mock.last_name = None
        user_mock.language_code = None

        parsed_data_mock = Mock()
        parsed_data_mock.user = user_mock
        parsed_data_mock.start_param = None

        mock_parse.return_value = parsed_data_mock
        init_data = "valid_init_data_string"

        result = auth_service.validate_init_data(init_data)

        assert isinstance(result, InitDataDTO)
        assert result.user_id == 67890
        assert result.username is None
        assert result.first_name == "Test"
        assert result.last_name is None
        assert result.start_param is None
        assert result.ui_language_code is None

    @patch("src.infrastructure.auth.safe_parse_webapp_init_data")
    def test_validate_init_data_parse_error(self, mock_parse, auth_service):
        mock_parse.side_effect = ValueError("Invalid data format")
        init_data = "invalid_init_data"

        with pytest.raises(
            InvalidInitDataError, match="Invalid init data 'invalid_init_data'"
        ):
            auth_service.validate_init_data(init_data)

    @patch("src.infrastructure.auth.safe_parse_webapp_init_data")
    def test_validate_init_data_missing_user(self, mock_parse, auth_service):
        parsed_data_mock = Mock()
        parsed_data_mock.user = None

        mock_parse.return_value = parsed_data_mock
        init_data = "init_data_without_user"

        with pytest.raises(
            ValidationError, match="Invalid init data 'init_data_without_user'"
        ):
            auth_service.validate_init_data(init_data)

    @pytest.mark.parametrize("user_id_value", [1, 999999999, 12345])
    def test_create_token_roundtrip(self, auth_service, mock_config, user_id_value):
        token = auth_service.create_access_token(user_id_value)
        decoded = Token.decode(
            encoded_token=token,
            secret=mock_config.auth.secret_key,
            algorithm=mock_config.auth.algorithm,
        )

        assert decoded.sub == str(user_id_value)


class TestInitDataDTO:
    def test_init_data_dto_creation(self):
        dto = InitDataDTO(
            user_id=12345,
            username="testuser",
            first_name="Test",
            last_name="User",
            start_param="start123",
            ui_language_code="en",
        )

        assert dto.user_id == 12345
        assert dto.username == "testuser"
        assert dto.first_name == "Test"
        assert dto.last_name == "User"
        assert dto.start_param == "start123"
        assert dto.ui_language_code == "en"

    def test_init_data_dto_with_none_values(self):
        dto = InitDataDTO(
            user_id=67890,
            username=None,
            first_name="Test",
            last_name=None,
            start_param=None,
            ui_language_code=None,
        )

        assert dto.user_id == 67890
        assert dto.username is None
        assert dto.first_name == "Test"
        assert dto.last_name is None
        assert dto.start_param is None
        assert dto.ui_language_code is None
