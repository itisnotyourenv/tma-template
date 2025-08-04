from dishka.integrations.litestar import FromDishka
from litestar import Request
from litestar.exceptions import NotAuthorizedException

from src.application.common.exceptions import ValidationError
from src.application.interfaces.auth import AuthService


def require_auth(request: Request, auth_service: FromDishka[AuthService]) -> int:
    """
    Dependency that validates JWT token from Authorization header.

    Returns:
        int: The authenticated user's ID

    Raises:
        NotAuthorizedException: If user is not authenticated or token is invalid
    """
    # Extract Bearer token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise NotAuthorizedException("Missing Authorization header")

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise NotAuthorizedException("Invalid Authorization header format")

    token = parts[1]

    try:
        user_id = auth_service.validate_access_token(token)
        return user_id
    except ValidationError as e:
        raise NotAuthorizedException(str(e))


def get_current_user_id(
    request: Request, auth_service: FromDishka[AuthService]
) -> int | None:
    """
    Optional dependency that returns user_id if authenticated, None otherwise.

    Returns:
        int | None: The authenticated user's ID or None if not authenticated
    """
    try:
        return require_auth(request, auth_service)
    except NotAuthorizedException:
        return None
