from aiogram import Router

from src.presentation.bot.filters import AdminFilter

from . import stats


def setup_routers() -> Router:
    router = Router(name="admin routers")
    router.message.filter(AdminFilter())
    router.callback_query.filter(AdminFilter())
    router.include_routers(
        stats.router,
    )
    return router
