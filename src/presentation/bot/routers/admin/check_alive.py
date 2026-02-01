from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from dishka.integrations.aiogram import FromDishka, inject

from src.application.admin import (
    CheckAliveInput,
    CheckAliveInteractor,
    CheckAliveResult,
)

router = Router(name="admin_check_alive")


def _build_filter_keyboard() -> InlineKeyboardMarkup:
    """Build keyboard with activity filter options."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="All Users", callback_data="check_alive:all"),
                InlineKeyboardButton(text="30 Days", callback_data="check_alive:30"),
            ],
            [
                InlineKeyboardButton(text="7 Days", callback_data="check_alive:7"),
                InlineKeyboardButton(text="1 Day", callback_data="check_alive:1"),
            ],
            [
                InlineKeyboardButton(text="Back", callback_data="admin:back_to_stats"),
            ],
        ],
    )


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


@router.callback_query(F.data == "check_alive")
async def cb_check_alive_menu(callback: CallbackQuery) -> None:
    """Show check alive filter options."""
    await callback.answer()
    await callback.message.edit_text(
        "Select users to check:",
        reply_markup=_build_filter_keyboard(),
    )


@router.callback_query(F.data.startswith("check_alive:"))
@inject
async def cb_check_alive_handler(
    callback: CallbackQuery,
    bot: Bot,
    interactor: FromDishka[CheckAliveInteractor],
) -> None:
    """Execute alive check with selected filter."""
    await callback.answer()

    # Parse filter from callback data
    filter_value = callback.data.split(":")[1]
    if filter_value == "all":
        active_since_days = None
        filter_label = "all users"
    else:
        active_since_days = int(filter_value)
        filter_label = f"users active in last {active_since_days} day(s)"

    await callback.message.edit_text(f"Starting alive check for {filter_label}...")

    last_result = None
    async for progress in interactor.execute(
        bot=bot, data=CheckAliveInput(active_since_days=active_since_days)
    ):
        last_result = progress.current_result
        await callback.message.edit_text(
            _format_progress(progress.processed, progress.total)
        )

    if last_result is None:
        await callback.message.edit_text(
            "No users found.", reply_markup=_build_back_button()
        )
        return

    await callback.message.edit_text(
        _format_result(last_result),
        reply_markup=_build_back_button(),
    )
