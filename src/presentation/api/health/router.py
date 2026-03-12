import logging

from litestar import Router, get

from src.presentation.api.health.schemas import (
    HealthCheckResponse,
    HealthCheckResponseSchema,
)

logger = logging.getLogger(__name__)


@get("/", return_dto=HealthCheckResponseSchema)
async def health_check_handler() -> HealthCheckResponse:
    return HealthCheckResponse()


health_router = Router(
    path="/health",
    route_handlers=[health_check_handler],
    tags=["health"],
)
