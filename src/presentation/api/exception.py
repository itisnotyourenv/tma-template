from http import HTTPStatus
import logging
from typing import Any

from litestar import Request, Response
from litestar.exceptions import ClientException
from pydantic import ValidationError as PydanticValidationError

from src.application.common.exceptions import ApplicationError, ValidationError
from src.presentation.api.base.schemas import CamelModel

logger = logging.getLogger(__name__)


class FieldError(CamelModel):
    field: str
    message: str


class ErrorResponse(CamelModel):
    detail: str
    status_code: int


class ValidationErrorResponse(CamelModel):
    detail: str
    status_code: int
    errors: list[FieldError]


def custom_exception_handler(
    _: Request[Any, Any, Any], exc: Exception
) -> Response[ErrorResponse]:
    logger.exception("Internal Server Error", exc_info=exc)

    return Response(
        ErrorResponse(
            detail="Internal Server Error",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        ),
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
    )


def litestar_error_handler(
    _: Request[Any, Any, Any], exc: ClientException
) -> Response[ErrorResponse]:
    return Response(
        ErrorResponse(detail=exc.detail, status_code=exc.status_code),
        status_code=exc.status_code,
    )


def exception_logs_handler(
    _: Request[Any, Any, Any], exc: ValidationError
) -> Response[ErrorResponse]:
    return Response(
        ErrorResponse(detail=exc.message, status_code=exc.status_code),
        status_code=exc.status_code,
    )


def validation_error_handler(
    _: Request[Any, Any, Any], exc: ValidationError
) -> Response[ErrorResponse]:
    return Response(
        ErrorResponse(detail=exc.message, status_code=exc.status_code),
        status_code=exc.status_code,
    )


def application_error_handler(
    _: Request[Any, Any, Any], exc: ApplicationError
) -> Response[ErrorResponse]:
    logger.exception(exc)

    return Response(
        ErrorResponse(detail=exc.message, status_code=exc.status_code),
        status_code=exc.status_code,
    )


def pydantic_validation_error_handler(
    _: Request[Any, Any, Any], exc: PydanticValidationError
) -> Response[ValidationErrorResponse]:
    field_errors = [
        FieldError(
            field=" -> ".join(str(loc) for loc in e["loc"]),
            message=e["msg"],
        )
        for e in exc.errors()
    ]
    return Response(
        ValidationErrorResponse(
            detail="Validation error",
            status_code=HTTPStatus.BAD_REQUEST,
            errors=field_errors,
        ),
        status_code=HTTPStatus.BAD_REQUEST,
    )


def value_error_handler(
    _: Request[Any, Any, Any], exc: ValueError | TypeError
) -> Response[ErrorResponse]:
    return Response(
        ErrorResponse(detail=str(exc), status_code=HTTPStatus.BAD_REQUEST),
        status_code=HTTPStatus.BAD_REQUEST,
    )
