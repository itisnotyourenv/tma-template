import asyncio
import logging
from collections.abc import AsyncGenerator
from dataclasses import dataclass

from aiogram import Bot
from aiogram.enums import ChatAction
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)

from src.domain.admin import AdminRepository

logger = logging.getLogger(__name__)

BATCH_SIZE = 20
PROGRESS_INTERVAL = 100


@dataclass
class CheckAliveResult:
    total: int = 0
    alive: int = 0
    blocked: int = 0
    deleted: int = 0
    rate_limited: int = 0
    other_errors: int = 0


@dataclass
class CheckAliveProgress:
    processed: int
    total: int
    current_result: CheckAliveResult


@dataclass
class CheckAliveInput:
    active_since_days: int | None = None


@dataclass
class UserCheckResult:
    user_id: int
    success: bool
    error_type: str | None = None


class CheckAliveInteractor:
    def __init__(self, admin_repository: AdminRepository) -> None:
        self._admin_repo = admin_repository

    async def _check_user(self, bot: Bot, user_id: int) -> UserCheckResult:
        """Check if a single user is alive by sending chat action."""
        try:
            await bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
            return UserCheckResult(user_id=user_id, success=True)
        except TelegramForbiddenError:
            return UserCheckResult(user_id=user_id, success=False, error_type="blocked")
        except TelegramBadRequest as e:
            if "chat not found" in str(e).lower():
                return UserCheckResult(
                    user_id=user_id, success=False, error_type="deleted"
                )
            logger.warning("TelegramBadRequest for user %d: %s", user_id, e)
            return UserCheckResult(user_id=user_id, success=False, error_type="other")
        except TelegramRetryAfter as e:
            logger.warning("Rate limited, waiting %d seconds", e.retry_after)
            await asyncio.sleep(e.retry_after)
            return UserCheckResult(
                user_id=user_id, success=False, error_type="rate_limited"
            )
        except Exception:
            logger.exception("Unexpected error checking user %d", user_id)
            return UserCheckResult(user_id=user_id, success=False, error_type="other")

    async def _process_batch(
        self, bot: Bot, user_ids: list[int]
    ) -> list[UserCheckResult]:
        """Process a batch of users concurrently."""
        tasks = [self._check_user(bot, user_id) for user_id in user_ids]
        return await asyncio.gather(*tasks)

    async def execute(
        self,
        bot: Bot,
        data: CheckAliveInput,
    ) -> AsyncGenerator[CheckAliveProgress]:
        """
        Execute the alive check and yield progress updates.

        Yields CheckAliveProgress every PROGRESS_INTERVAL users.
        """
        user_ids = await self._admin_repo.get_all_user_ids(
            active_since_days=data.active_since_days,
        )
        total = len(user_ids)
        result = CheckAliveResult(total=total)
        processed = 0

        for i in range(0, total, BATCH_SIZE):
            batch = user_ids[i : i + BATCH_SIZE]
            batch_results = await self._process_batch(bot, batch)

            for check_result in batch_results:
                if check_result.success:
                    result.alive += 1
                elif check_result.error_type == "blocked":
                    result.blocked += 1
                elif check_result.error_type == "deleted":
                    result.deleted += 1
                elif check_result.error_type == "rate_limited":
                    result.rate_limited += 1
                else:
                    result.other_errors += 1

            processed += len(batch)

            if processed % PROGRESS_INTERVAL < BATCH_SIZE or processed == total:
                yield CheckAliveProgress(
                    processed=processed,
                    total=total,
                    current_result=result,
                )
