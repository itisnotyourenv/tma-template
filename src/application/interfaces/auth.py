from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol


@dataclass
class InitDataDTO:
    user_id: int
    username: str | None
    first_name: str
    last_name: str | None
    start_param: str | None
    ui_language_code: str | None


class AuthService(Protocol):
    @abstractmethod
    def validate_init_data(self, init_data: str) -> InitDataDTO: ...

    @abstractmethod
    def create_access_token(self, user_id: int) -> str: ...
