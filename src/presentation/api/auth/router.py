import logging

from dishka.integrations.litestar import FromDishka, inject
from litestar import Router, post

from src.application.auth.tg import AuthTgInputDTO, AuthTgInteractor, AuthTgOutputDTO
from src.presentation.api.auth.schemas import AuthTgRequest

logger = logging.getLogger(__name__)


@post("/")
@inject
async def auth_user_handler(
    data: AuthTgRequest,
    interactor: FromDishka[AuthTgInteractor],
) -> AuthTgOutputDTO:
    response = await interactor(AuthTgInputDTO(data.init_data))
    return response


auth_router = Router(
    path="/auth",
    route_handlers=[auth_user_handler],
    tags=["auth"],
)
