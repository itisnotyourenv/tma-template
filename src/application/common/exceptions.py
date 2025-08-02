from dataclasses import dataclass
from http import HTTPStatus


@dataclass
class ApplicationError(Exception):
    status_code: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


@dataclass
class ValidationError(ApplicationError):
    status_code: HTTPStatus = 400
    message: str = "something went wrong"
