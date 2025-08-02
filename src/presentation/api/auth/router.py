import logging

from dishka.integrations.litestar import inject, FromDishka
from litestar import Router, post

from src.application.auth.tg import AuthTgInteractor, AuthTgInputDTO
from src.presentation.api.auth.schemas import AuthTgRequest

logger = logging.getLogger(__name__)


@post("/")
@inject
async def auth_user_handler(
    data: AuthTgRequest,
    interactor: FromDishka[AuthTgInteractor],
) -> dict:
    await interactor(AuthTgInputDTO('iasdfadsf'))
    return {"success": True, "message": "Service is healthy"}


auth_router = Router(
    path="/auth",
    route_handlers=[auth_user_handler],
    tags=["auth"],
)
