from litestar import Request
from litestar.exceptions import HTTPException

from src.domain.user.vo import UserId


def provide_user_id(request: Request) -> UserId:
    try:
        user_id = request.scope.get("user", None)
        if user_id is None:
            raise HTTPException(status_code=401, detail="User ID header is required")
        return UserId(int(user_id))
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid UserID header value. Must be an integer."
        ) from None
