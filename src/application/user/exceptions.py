from http import HTTPStatus

from src.application.common.exceptions import ApplicationError
from src.domain.user.vo import UserId


class UserNotFoundError(ApplicationError):
    status_code: HTTPStatus = HTTPStatus.NOT_FOUND

    def __init__(self, user_id: UserId) -> None:
        super().__init__(f"User {user_id.value} not found")
        self.user_id = user_id
