from aiogram.types import CallbackQuery, InaccessibleMessage, Message


async def process_inaccessible_message(callback: CallbackQuery) -> Message | None:
    """Check if the message is inaccessible (e.g., deleted or user blocked)."""
    if isinstance(callback.message, InaccessibleMessage):
        await callback.answer(
            "Cannot perform check: the message is inaccessible. Please navigate back to stats and try again.",
            show_alert=True,
        )

        return None

    return callback.message
