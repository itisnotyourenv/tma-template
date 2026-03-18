from typing import cast

from aiogram import Bot, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from dishka.integrations.aiogram import FromDishka, inject

from src.application.admin import (
    CheckAliveInput,
    CheckAliveInteractor,
    CheckAliveResult,
)
from src.presentation.bot.utils.admin_cb_data import (
    CheckAliveCBData,
    CheckAliveCBFilter,
)

router = Router(name="admin_check_alive")


def _build_back_button() -> InlineKeyboardMarkup:
    """Build back button to return to stats."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Back to Stats", callback_data="admin:back_to_stats"
                )
            ],
        ],
    )


def _format_progress(processed: int, total: int) -> str:
    """Format progress message during check."""
    percent = (processed / total * 100) if total > 0 else 0
    return f"Checking alive users...\n\nProgress: {processed}/{total} ({percent:.1f}%)"


def _format_result(result: CheckAliveResult) -> str:
    """Format final result message."""
    total = result.total
    if total == 0:
        return "No users to check."

    alive_pct = result.alive / total * 100
    blocked_pct = result.blocked / total * 100
    deleted_pct = result.deleted / total * 100
    other_pct = result.other_errors / total * 100

    lines = [
        "Check Complete!\n",
        f"Total users: {total}",
        f"Alive: {result.alive} ({alive_pct:.1f}%)",
        f"Blocked bot: {result.blocked} ({blocked_pct:.1f}%)",
        f"Deleted account: {result.deleted} ({deleted_pct:.1f}%)",
    ]

    if result.other_errors > 0:
        lines.append(f"Other errors: {result.other_errors} ({other_pct:.1f}%)")

    if result.rate_limited > 0:
        lines.append(f"\nRate limited retries: {result.rate_limited}")

    return "\n".join(lines)


@router.callback_query(CheckAliveCBData.filter())
@inject
async def cb_check_alive_handler(
    callback: CallbackQuery,
    callback_data: CheckAliveCBData,
    bot: Bot,
    interactor: FromDishka[CheckAliveInteractor],
) -> None:
    """Execute alive check with selected filter."""
    await callback.answer()

    # Parse filter from callback data
    filter_value = callback_data.filter_
    if filter_value == CheckAliveCBFilter.ALL:
        active_since_days = None
        filter_label = "all users"
    else:
        active_since_days = int(filter_value.value)
        filter_label = f"users active in last {active_since_days} day(s)"

    await cast(Message, callback.message).edit_text(
        f"Starting alive check for {filter_label}..."
    )

    last_result = None
    async for progress in interactor.execute(
        bot=bot, data=CheckAliveInput(active_since_days=active_since_days)
    ):
        last_result = progress.current_result
        await cast(Message, callback.message).edit_text(
            _format_progress(progress.processed, progress.total)
        )

    if last_result is None:
        await cast(Message, callback.message).edit_text(
            "No users found.", reply_markup=_build_back_button()
        )
        return

    await cast(Message, callback.message).edit_text(
        _format_result(last_result),
        reply_markup=_build_back_button(),
    )
