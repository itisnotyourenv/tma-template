import logging

from dishka.integrations.litestar import FromDishka, inject
from litestar import Router, get

from src.application.user.get_me import (
    GetUserProfileInputDTO,
    GetUserProfileInteractor,
    GetUserProfileOutputDTO,
)
from src.domain.user.vo import UserId
from src.presentation.api.user.schemas import UserProfileResponseSchema

logger = logging.getLogger(__name__)


@get("/profile", return_dto=UserProfileResponseSchema)
@inject
async def get_user_profile(
    user_id: UserId,
    interactor: FromDishka[GetUserProfileInteractor],
) -> GetUserProfileOutputDTO:
    """
    Get the authenticated user's profile.

    Requires valid JWT token in Authorization header.
    """
    response = await interactor(data=GetUserProfileInputDTO(user_id=user_id))

    return response


user_router = Router(
    path="/users",
    route_handlers=[get_user_profile],
    tags=["users"],
)
