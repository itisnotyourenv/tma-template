import logging

from dishka.integrations.litestar import inject, FromDishka
from litestar import Router, get
from litestar.exceptions import NotFoundException

from src.domain.user import UserRepository
from src.domain.user.vo import UserId
from src.presentation.api.user.schemas import UserProfileResponse

logger = logging.getLogger(__name__)


@get("/profile")
@inject
async def get_user_profile(
    user_id: UserId,
    user_repository: FromDishka[UserRepository],
) -> UserProfileResponse:
    """
    Get the authenticated user's profile.

    Requires valid JWT token in Authorization header.
    """
    user = await user_repository.get_user(user_id.value, by="id")

    if user is None:
        raise NotFoundException("User not found")

    return UserProfileResponse(
        id=user.id.value,
        first_name=user.first_name.value,
        last_name=user.last_name.value if user.last_name else None,
        username=user.username.value if user.username else None,
        bio=user.bio.value if user.bio else None,
    )


user_router = Router(
    path="/users",
    route_handlers=[get_user_profile],
    tags=["users"],
)
