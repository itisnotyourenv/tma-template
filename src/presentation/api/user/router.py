import logging
from typing import Any

from dishka.integrations.litestar import FromDishka, inject
from litestar import Request, Router, get
from litestar.security.jwt import Token

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
    request: Request[UserId, Token, Any],
    interactor: FromDishka[GetUserProfileInteractor],
) -> GetUserProfileOutputDTO:
    """Get the authenticated user's profile."""
    response = await interactor(data=GetUserProfileInputDTO(user_id=request.user))

    return response


user_router = Router(
    path="/users",
    route_handlers=[get_user_profile],
    tags=["users"],
)
