import logging
from typing import Sequence

from litestar.connection import ASGIConnection
from litestar.datastructures import Headers
from litestar.exceptions import NotAuthorizedException
from litestar.middleware import AbstractAuthenticationMiddleware, AuthenticationResult
from litestar.types import ASGIApp, Method, Scopes

from src.application.common.exceptions import ValidationError
from src.application.interfaces.auth import AuthService
from src.infrastructure.auth import AuthServiceImpl
from src.infrastructure.config import Config

logger = logging.getLogger(__name__)


class AuthMiddleware(AbstractAuthenticationMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        auth_service: AuthService,
        exclude: str | list[str] | None = None,
        exclude_from_auth_key: str = "exclude_from_auth",
        exclude_http_methods: Sequence[Method] | None = None,
        scopes: Scopes = None,
    ) -> None:
        """Initialize ``AbstractAuthenticationMiddleware``.

        Args:
            app: An ASGIApp, this value is the next ASGI handler to call in the middleware stack.
            exclude: A pattern or list of patterns to skip in the authentication middleware.
            exclude_from_auth_key: An identifier to use on routes to disable authentication for a particular route.
            exclude_http_methods: A sequence of http methods that do not require authentication.
            scopes: ASGI scopes processed by the authentication middleware.
        """
        self.auth_service: AuthService = auth_service
        super().__init__(
            app, exclude, exclude_from_auth_key, exclude_http_methods, scopes
        )

    async def authenticate_request(
        self, connection: ASGIConnection
    ) -> AuthenticationResult:
        """Receive the http connection and return an :class:`AuthenticationResult`.

        Notes:
            - This method must be overridden by subclasses.

        Args:
            connection: An :class:`ASGIConnection <litestar.connection.ASGIConnection>` instance.

        Raises:
            NotAuthorizedException | PermissionDeniedException: if authentication fails.

        Returns:
            An instance of :class:`AuthenticationResult <litestar.middleware.authentication.AuthenticationResult>`.
        """
        try:
            token = self._extract_bearer_token(connection.headers)
            if token:
                user_id = self.auth_service.validate_access_token(token)
                # Add authenticated user_id to request state
                return AuthenticationResult(user=user_id, auth=token)
            else:
                # No token provided for protected route
                raise NotAuthorizedException

        except ValidationError as e:
            # Invalid or expired token
            raise NotAuthorizedException(detail=str(e))

    @staticmethod
    def _extract_bearer_token(headers: Headers) -> str | None:
        """Extract Bearer token from Authorization header."""
        auth_header = headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix
        return None
