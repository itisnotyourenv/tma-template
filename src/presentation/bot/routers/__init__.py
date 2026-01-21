from aiogram import Router

from .admin import setup_routers as setup_admin_routers
from .commands import router as commands_router


def setup_routers() -> Router:
    """Set up all bot routers."""
    main_router = Router()

    # Command handlers first (highest priority)
    main_router.include_routers(
        commands_router,
        setup_admin_routers(),
    )

    return main_router


__all__ = ["setup_routers"]
