from litestar import Litestar

from .health import health_router
from .auth import auth_router


def create_app() -> Litestar:
    return Litestar(
        route_handlers=[
            auth_router,
            health_router,
        ],
    )
