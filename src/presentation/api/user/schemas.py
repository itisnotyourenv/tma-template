from src.application.user.get_me import GetUserProfileOutputDTO
from src.presentation.api.base.schemas import BaseResponseDTO


class UserProfileResponseSchema(BaseResponseDTO[GetUserProfileOutputDTO]): ...
