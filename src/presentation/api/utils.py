from litestar import Router

from .auth import auth_router
from .health import health_router

def setup_routes() -> Router:
    route_handlers = [
        auth_router,
        health_router,
    ]
    router = Router(path="", route_handlers=route_handlers)
    return router
