from abc import abstractmethod
from typing import Protocol


class AdminRepository(Protocol):
    @abstractmethod
    async def get_all_user_ids(self, active_since_days: int | None = None) -> list[int]:
        """
        Get all user IDs, optionally filtered by recent activity.

        Args:
            active_since_days: If provided, only return users who logged in
                              within the last N days. None means all users.

        Returns:
            List of Telegram user IDs.
        """
        raise NotImplementedError
