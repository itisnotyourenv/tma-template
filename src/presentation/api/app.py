from dishka import make_async_container
from litestar import Litestar
from dishka.integrations.litestar import setup_dishka
from litestar.di import Provide
from litestar.exceptions import ClientException
from litestar.middleware import DefineMiddleware

from src.application.common.exceptions import ValidationError
from src.infrastructure.config import load_config, Config
from src.infrastructure.di.auth import AuthProvider
from src.infrastructure.di import interactor_providers
from src.infrastructure.di.db import DBProvider
from src.application.auth.exceptions import InvalidInitDataError


from .exception import (
    custom_exception_handler,
    validation_error_handler,
    exception_logs_handler,
    litestar_error_handler,
)
from .middleware.auth import AuthMiddleware
from .providers import provide_user_id
from .utils import setup_routes
from ...infrastructure.auth import AuthServiceImpl


def prepare_app(config: Config) -> Litestar:
    routes = setup_routes()

    auth_service = AuthServiceImpl(config)

    app = Litestar(
        route_handlers=[
            routes,
        ],
        exception_handlers={
            Exception: custom_exception_handler,
            ClientException: litestar_error_handler,
            InvalidInitDataError: exception_logs_handler,
            ValidationError: validation_error_handler,
        },
        middleware=[DefineMiddleware(AuthMiddleware, exclude=['auth', 'health'], auth_service=auth_service)],
        dependencies={
            # todo - rewrite with Dishka
            "user_id": Provide(provide_user_id, sync_to_thread=False)
        }
    )
    return app


def create_app() -> Litestar:
    config = load_config()

    app = prepare_app(config)

    interactor_provider_instances = [
        interactor() for interactor in interactor_providers
    ]

    container = make_async_container(
        AuthProvider(),
        DBProvider(config.postgres),  # todo - pass config with context
        *interactor_provider_instances,
        context={Config: config},
    )

    setup_dishka(container=container, app=app)
    return app
