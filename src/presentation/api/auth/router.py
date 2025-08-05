import logging

from dishka.integrations.litestar import FromDishka, inject
from litestar import Router, post

from src.application.auth.tg import AuthTgInputDTO, AuthTgInteractor
from src.presentation.api.auth.schemas import AuthTgRequest

logger = logging.getLogger(__name__)


@post("/")
@inject
async def auth_user_handler(
    data: AuthTgRequest,
    interactor: FromDishka[AuthTgInteractor],
) -> dict:
    response = await interactor(AuthTgInputDTO(data.init_data))
    return response


auth_router = Router(
    path="/auth",
    route_handlers=[auth_user_handler],
    tags=["auth"],
)
