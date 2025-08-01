import logging

from litestar import Request, Router, post

from src.presentation.api.auth.schemas import AuthTgRequest

logger = logging.getLogger(__name__)


@post("/")
async def auth_user_handler(
        data: AuthTgRequest
) -> dict:
    return {"success": True, "message": "Service is healthy"}


auth_router = Router(
    path="/auth",
    route_handlers=[auth_user_handler],
    tags=["auth"],
)
