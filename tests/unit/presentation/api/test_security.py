from datetime import UTC, datetime, timedelta
from unittest.mock import Mock

from litestar import Request
from litestar.exceptions import NotAuthorizedException
from litestar.security.jwt import Token
import pytest

from src.domain.user.vo import UserId
from src.infrastructure.config import Config
from src.presentation.api.security import (
    OPTIONAL_AUTH_ROUTE,
    PUBLIC_ROUTE,
    SCHEMA_AUTH_EXCLUDE_PATTERNS,
    create_jwt_auth,
    decode_token_to_user_id,
    get_optional_user_from_request,
)


@pytest.fixture
def mock_config() -> Mock:
    config = Mock(spec=Config)
    auth_config = Mock()
    auth_config.secret_key = "3d1b2a2127de6f65804364813b3107b2"
    auth_config.algorithm = "HS256"
    config.auth = auth_config
    return config


def _create_token(config: Config, sub: str = "12345") -> str:
    token = Token(
        sub=sub,
        exp=datetime.now(UTC) + timedelta(minutes=30),
    )
    return token.encode(
        secret=config.auth.secret_key,
        algorithm=config.auth.algorithm,
    )


def _create_request(auth_header: str | None) -> Mock:
    request = Mock(spec=Request)
    request.headers = {}
    if auth_header is not None:
        request.headers["Authorization"] = auth_header
    return request


class TestRouteSecurityOptions:
    def test_public_route_marks_operation_anonymous(self) -> None:
        assert PUBLIC_ROUTE == {
            "exclude_from_auth": True,
            "security": [{}],
        }

    def test_optional_auth_route_marks_operation_optional(self) -> None:
        assert OPTIONAL_AUTH_ROUTE == {
            "exclude_from_auth": True,
            "security": [{}, {"BearerToken": []}],
        }


class TestJWTAuthFactory:
    def test_create_jwt_auth_uses_configured_bearer_scheme(
        self, mock_config: Mock
    ) -> None:
        jwt_auth = create_jwt_auth(mock_config)

        assert jwt_auth.token_secret == mock_config.auth.secret_key
        assert jwt_auth.algorithm == mock_config.auth.algorithm
        assert jwt_auth.exclude == SCHEMA_AUTH_EXCLUDE_PATTERNS
        assert jwt_auth.openapi_security_scheme_name == "BearerToken"


class TestTokenDecoding:
    def test_decode_token_to_user_id_success(self, mock_config: Mock) -> None:
        token = _create_token(mock_config)

        user_id = decode_token_to_user_id(token, mock_config)

        assert user_id == UserId(12345)

    def test_decode_token_to_user_id_rejects_invalid_subject(
        self, mock_config: Mock
    ) -> None:
        token = _create_token(mock_config, sub="not-an-int")

        with pytest.raises(NotAuthorizedException, match="Invalid token subject"):
            decode_token_to_user_id(token, mock_config)


class TestOptionalRequestAuth:
    def test_missing_bearer_token_returns_anonymous(self, mock_config: Mock) -> None:
        request = _create_request(auth_header=None)

        user_id = get_optional_user_from_request(request, mock_config)

        assert user_id is None

    def test_valid_bearer_token_returns_user_id(self, mock_config: Mock) -> None:
        request = _create_request(
            auth_header=f"Bearer {_create_token(mock_config, sub='67890')}"
        )

        user_id = get_optional_user_from_request(request, mock_config)

        assert user_id == UserId(67890)

    def test_malformed_authorization_header_returns_401(
        self, mock_config: Mock
    ) -> None:
        request = _create_request(auth_header="InvalidFormat token")

        with pytest.raises(
            NotAuthorizedException, match="Invalid Authorization header"
        ):
            get_optional_user_from_request(request, mock_config)

    def test_invalid_bearer_token_returns_401(self, mock_config: Mock) -> None:
        request = _create_request(auth_header="Bearer invalid.token.value")

        with pytest.raises(NotAuthorizedException, match="Invalid token"):
            get_optional_user_from_request(request, mock_config)
