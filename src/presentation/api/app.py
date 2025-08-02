from dishka import make_async_container
from litestar import Litestar
from dishka.integrations.litestar import setup_dishka

from src.application.common.exceptions import ValidationError
from src.infrastructure.config import load_config, Config
from src.infrastructure.di.auth import AuthProvider
from src.infrastructure.di.interactors.auth import AuthInteractorProvider
from src.infrastructure.di.db import DBProvider

from .auth import auth_router
from .exception import custom_exception_handler, validation_error_handler
from .health import health_router


def create_app() -> Litestar:
    config = load_config()

    app = Litestar(
        route_handlers=[
            auth_router,
            health_router,
        ],
        exception_handlers={
            Exception: custom_exception_handler,
            ValidationError: validation_error_handler,
        }
    )

    container = make_async_container(
        AuthProvider(),
        AuthInteractorProvider(),
        DBProvider(config.postgres),
        context={Config: config},
    )

    setup_dishka(container=container, app=app)
    return app
