from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup


async def edit_or_answer(
    update: types.Message | types.CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """
    Attempts to edit the message if it's a callback query,
    otherwise sends a new message.
    """
    try:
        if isinstance(update, types.CallbackQuery) and update.message:
            await update.message.edit_text(text, reply_markup=reply_markup)
        else:
            await update.answer(text, reply_markup=reply_markup)
    except TelegramBadRequest:
        # Fallback if editing fails (e.g., message content is identical)
        await update.answer(text, reply_markup=reply_markup)
