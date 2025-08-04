import logging
from typing import Any

from litestar import Request, Response
from litestar.exceptions import ClientException

from src.application.common.exceptions import ValidationError

logger = logging.getLogger(__name__)


def custom_exception_handler(
    _: Request[Any, Any, Any], exc: Exception
) -> Response[Any]:
    logger.exception(exc)
    return Response(
        {"detail": "Internal Server Error", "status_code": 500}, status_code=500
    )


def litestar_error_handler(
    _: Request[Any, Any, Any], exc: ClientException
) -> Response[Any]:
    logger.info(exc)
    return Response(
        {"detail": exc.detail, "extra": exc.extra, "status_code": exc.status_code},
        status_code=exc.status_code,
    )


def exception_logs_handler(
    _: Request[Any, Any, Any], exc: ValidationError
) -> Response[Any]:
    logger.warning(exc)
    return Response(
        {"detail": exc.message, "status_code": exc.status_code},
        status_code=exc.status_code,
    )


def validation_error_handler(
    _: Request[Any, Any, Any], exc: ValidationError
) -> Response[Any]:
    logger.exception(exc)
    return Response(
        {"detail": exc.message, "status_code": exc.status_code},
        status_code=exc.status_code,
    )
