from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from dishka.integrations.aiogram import FromDishka, inject
from fluentogram import TranslatorHub

from src.application.referral.stats import GetStatsInteractor, GetTopReferrersInteractor
from src.presentation.bot.utils.i18n import extract_language_code

router = Router(name="admin_stats")


@router.message(Command("stats"))
@inject
async def stats_handler(
    message: Message,
    hub: FromDishka[TranslatorHub],
    interactor: FromDishka[GetStatsInteractor],
) -> None:
    """Handle /stats admin command."""
    locale = extract_language_code(message.from_user.language_code)
    i18n = hub.get_translator_by_locale(locale)

    stats = await interactor()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("stats-top-inviters-btn"),
                    callback_data="ref_top",
                )
            ]
        ]
    )

    await message.answer(
        text=i18n.get(
            "stats-overview",
            total=stats.total_users,
            referred=stats.referred_count,
            referred_pct=stats.referred_percent,
            organic=stats.organic_count,
            organic_pct=stats.organic_percent,
        ),
        reply_markup=keyboard,
    )


@router.callback_query(F.data == "ref_top")
@inject
async def ref_top_callback(
    callback: CallbackQuery,
    hub: FromDishka[TranslatorHub],
    interactor: FromDishka[GetTopReferrersInteractor],
) -> None:
    """Handle top referrers callback."""
    locale = extract_language_code(callback.from_user.language_code)
    i18n = hub.get_translator_by_locale(locale)

    limit = 10
    top = await interactor(limit)

    if not top:
        await callback.message.edit_text(text=i18n.get("stats-no-inviters"))
        await callback.answer()
        return

    text = i18n.get("stats-top-inviters-header", limit=limit) + "\n\n"
    for i, ref in enumerate(top, 1):
        name = f"@{ref.username}" if ref.username else ref.first_name
        text += f"{i}. {name} — {ref.count}\n"

    await callback.message.edit_text(text=text)
    await callback.answer()
