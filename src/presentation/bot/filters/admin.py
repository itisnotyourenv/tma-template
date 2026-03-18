from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message

from src.infrastructure.config import Config


class AdminFilter(Filter):
    async def __call__(self, obj: Message | CallbackQuery, config: Config) -> bool:
        """
        Args:
            obj (Update): Aiogram injects it to the the filter.
            config (Config): Aiogram injects it to the the filter.
        """
        if obj.from_user is None:
            return False

        return obj.from_user.id in config.telegram.admin_ids
