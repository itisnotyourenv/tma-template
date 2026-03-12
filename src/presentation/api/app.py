from dishka import make_async_container
from dishka.integrations.litestar import setup_dishka
from litestar import Litestar
from litestar.di import Provide
from litestar.exceptions import ClientException, NotAuthorizedException
from litestar.middleware import DefineMiddleware
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from pydantic import ValidationError as PydanticValidationError

from src.application.auth.exceptions import InvalidInitDataError
from src.application.common.exceptions import ApplicationError, ValidationError
from src.application.interfaces.auth import AuthService
from src.infrastructure.auth import AuthServiceImpl
from src.infrastructure.config import Config, load_config
from src.infrastructure.di import interactor_providers
from src.infrastructure.di.auth import AuthProvider
from src.infrastructure.di.db import DBProvider

from .exception import (
    application_error_handler,
    custom_exception_handler,
    exception_logs_handler,
    litestar_error_handler,
    pydantic_validation_error_handler,
    validation_error_handler,
    value_error_handler,
)
from .middleware.auth import AuthMiddleware
from .providers import provide_user_id
from .utils import setup_routes

PUBLIC_AUTH_EXCLUDE_PATTERNS = [
    r"^/auth(?:/|$)",
    r"^/health(?:/|$)",
    r"^/schema(?:/|$)",
]


def prepare_app(auth_service: AuthService) -> Litestar:
    routes = setup_routes()

    app = Litestar(
        route_handlers=[routes],
        openapi_config=OpenAPIConfig(
            title="TG app API",
            description="API for TG app",
            version="0.1.0",
            render_plugins=[ScalarRenderPlugin()],
        ),
        exception_handlers={
            Exception: custom_exception_handler,
            NotAuthorizedException: litestar_error_handler,
            ClientException: litestar_error_handler,
            ApplicationError: application_error_handler,
            ValidationError: validation_error_handler,
            PydanticValidationError: pydantic_validation_error_handler,
            ValueError: value_error_handler,
            TypeError: value_error_handler,
            InvalidInitDataError: exception_logs_handler,
        },
        middleware=[
            DefineMiddleware(
                AuthMiddleware,
                exclude=PUBLIC_AUTH_EXCLUDE_PATTERNS,
                auth_service=auth_service,
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

    auth_service: AuthService = AuthServiceImpl(config)
    app = prepare_app(auth_service)

    interactor_provider_instances = [
        interactor() for interactor in interactor_providers
    ]

    container = make_async_container(
        AuthProvider(),
        DBProvider(),
        *interactor_provider_instances,
        context={Config: config, AuthService: auth_service},
    )

    setup_dishka(container=container, app=app)
    return app
