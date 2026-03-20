from dishka import make_async_container
from dishka.integrations.litestar import setup_dishka
from litestar import Litestar
from litestar.exceptions import ClientException, NotAuthorizedException
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
from .security import create_jwt_auth
from .utils import setup_routes


def prepare_app(config: Config) -> Litestar:
    routes = setup_routes()
    jwt_auth = create_jwt_auth(config)

    return Litestar(
        route_handlers=[routes],
        on_app_init=[jwt_auth.on_app_init],
        openapi_config=OpenAPIConfig(
            title="TMA API",
            description="API for TMA",
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
    )


def create_app() -> Litestar:
    config = load_config()

    auth_service: AuthService = AuthServiceImpl(config)
    app = prepare_app(config)

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
