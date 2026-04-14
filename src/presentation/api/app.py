from dishka import make_async_container
from dishka.integrations.litestar import setup_dishka
from litestar import Litestar
from litestar.di import Provide
from litestar.exceptions import ClientException
from litestar.middleware import DefineMiddleware

from src.application.auth.exceptions import InvalidInitDataError
from src.application.common.exceptions import ValidationError
from src.application.interfaces.auth import AuthService
from src.infrastructure.auth import AuthServiceImpl
from src.infrastructure.config import Config, load_config
from src.infrastructure.di import infra_providers, interactor_providers
from src.infrastructure.sentry import init_sentry

from .exception import (
    custom_exception_handler,
    exception_logs_handler,
    litestar_error_handler,
    validation_error_handler,
)
from .middleware.auth import AuthMiddleware
from .providers import provide_user_id
from .utils import setup_routes


def prepare_app(auth_service: AuthService) -> Litestar:
    routes = setup_routes()

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
        middleware=[
            DefineMiddleware(
                AuthMiddleware, exclude=["auth", "health"], auth_service=auth_service
            )
        ],
        dependencies={
            # todo - rewrite with Dishka
            "user_id": Provide(provide_user_id, sync_to_thread=False)
        },
    )
    return app


def create_app() -> Litestar:
    config = load_config()
    init_sentry(config)

    auth_service: AuthService = AuthServiceImpl(config)
    app = prepare_app(auth_service)

    container = make_async_container(
        *infra_providers,
        *interactor_providers,
        context={Config: config, AuthService: auth_service},
    )

    setup_dishka(container=container, app=app)
    return app
