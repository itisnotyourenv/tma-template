from http import HTTPStatus


class ApplicationError(Exception):
    status_code: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class ValidationError(ApplicationError):
    status_code: HTTPStatus = HTTPStatus.BAD_REQUEST
