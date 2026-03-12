from dataclasses import dataclass

from src.application.auth.tg import AuthTgOutputDTO
from src.presentation.api.base.schemas import BaseRequestDTO, BaseResponseDTO


@dataclass
class AuthTgRequest:
    init_data: str


class AuthTgRequestSchema(BaseRequestDTO[AuthTgRequest]): ...


class AuthTgResponseSchema(BaseResponseDTO[AuthTgOutputDTO]): ...
