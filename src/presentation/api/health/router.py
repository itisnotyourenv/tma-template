import logging

from litestar import Request, Router, get

logger = logging.getLogger(__name__)


@get("/")
async def health_check_handler(request: Request) -> dict:
    return {"success": True, "message": "Service is healthy"}


health_router = Router(
    path="/health",
    route_handlers=[health_check_handler],
    tags=["health"],
)
