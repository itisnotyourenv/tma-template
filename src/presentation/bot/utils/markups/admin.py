from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.infrastructure.i18n import TranslatorRunner


def stats_main_markup(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.stats_top_inviters_btn(),
                    callback_data="ref_top",
                ),
                InlineKeyboardButton(
                    text=i18n.check_alive_btn(),
                    callback_data="check_alive",
                ),
            ]
        ]
    )
