from typing import Any

from litestar import Request
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.security.jwt import JWTAuth, Token

from src.domain.user.vo import UserId
from src.infrastructure.config import Config

PUBLIC_ROUTE: dict[str, Any] = {
    "exclude_from_auth": True,
    "security": [{}],
}
OPTIONAL_AUTH_ROUTE: dict[str, Any] = {
    "exclude_from_auth": True,
    "security": [{}, {"BearerToken": []}],
}
SCHEMA_AUTH_EXCLUDE_PATTERNS = [r"^/schema(?:/|$)"]


def _user_id_from_subject(subject: str) -> UserId:
    try:
        return UserId(int(subject))
    except (TypeError, ValueError) as exc:
        raise NotAuthorizedException("Invalid token subject") from exc


def user_id_from_token(token: Token) -> UserId:
    return _user_id_from_subject(token.sub)


def decode_token_to_user_id(encoded_token: str, config: Config) -> UserId:
    token = Token.decode(
        encoded_token=encoded_token,
        secret=config.auth.secret_key,
        algorithm=config.auth.algorithm,
    )
    return user_id_from_token(token)


def _extract_optional_bearer_token(auth_header: str | None) -> str | None:
    if auth_header is None:
        return None
    if not auth_header.lower().startswith("bearer "):
        raise NotAuthorizedException("Invalid Authorization header")

    encoded_token = auth_header[7:]
    if not encoded_token:
        raise NotAuthorizedException("Invalid token")
    return encoded_token


def get_optional_user_from_request(
    request: Request[Any, Any, Any], config: Config
) -> UserId | None:
    """Authenticate an optional-auth request only when a bearer token is present."""
    encoded_token = _extract_optional_bearer_token(request.headers.get("Authorization"))
    if encoded_token is None:
        return None

    return decode_token_to_user_id(encoded_token=encoded_token, config=config)


def create_jwt_auth(config: Config) -> JWTAuth[UserId, Token]:
    def retrieve_user_handler(
        token: Token, _: ASGIConnection[Any, Any, Any, Any]
    ) -> UserId:
        return user_id_from_token(token)

    return JWTAuth[
        UserId,
        Token,
    ](
        token_secret=config.auth.secret_key,
        algorithm=config.auth.algorithm,
        retrieve_user_handler=retrieve_user_handler,
        exclude=SCHEMA_AUTH_EXCLUDE_PATTERNS,
    )
