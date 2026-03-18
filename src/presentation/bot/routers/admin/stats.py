from typing import cast

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    User,
)
from dishka.integrations.aiogram import FromDishka, inject
from fluentogram import TranslatorHub

from src.application.referral.stats import GetStatsInteractor, GetTopReferrersInteractor
from src.presentation.bot.utils.admin_cb_data import (
    CheckAliveCBData,
    CheckAliveCBFilter,
    StatsCBAction,
    StatsCBData,
)
from src.presentation.bot.utils.i18n import extract_language_code
from src.presentation.bot.utils.inaccessible_message import process_inaccessible_message

router = Router(name="admin_stats")


@router.message(Command("stats"))
@inject
async def stats_handler(
    message: Message,
    hub: FromDishka[TranslatorHub],
    interactor: FromDishka[GetStatsInteractor],
) -> None:
    """Handle /stats admin command."""
    locale = extract_language_code(cast(User, message.from_user).language_code)
    i18n = hub.get_translator_by_locale(locale)

    stats = await interactor()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("stats-top-inviters-btn"),
                    callback_data=StatsCBData(
                        action=StatsCBAction.TOP_REFERRERS
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="Check Alive",
                    callback_data=StatsCBData(action=StatsCBAction.CHECK_ALIVE).pack(),
                ),
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


@router.callback_query(StatsCBData.filter(F.action == StatsCBAction.TOP_REFERRERS))
@inject
async def ref_top_callback(
    callback: CallbackQuery,
    hub: FromDishka[TranslatorHub],
    interactor: FromDishka[GetTopReferrersInteractor],
) -> None:
    """Handle top referrers callback."""
    if not (message := await process_inaccessible_message(callback)):
        return

    locale = extract_language_code(callback.from_user.language_code)
    i18n = hub.get_translator_by_locale(locale)

    limit = 10
    top = await interactor(limit)

    if not top:
        await message.edit_text(text=i18n.get("stats-no-inviters"))
        await callback.answer()
        return

    text = i18n.get("stats-top-inviters-header", limit=limit) + "\n\n"
    for i, ref in enumerate(top, 1):
        name = f"@{ref.username}" if ref.username else ref.first_name
        text += f"{i}. {name} — {ref.count}\n"

    await message.edit_text(text=text)
    await callback.answer()


check_alive_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="All Users",
                callback_data=CheckAliveCBData(filter_=CheckAliveCBFilter.ALL).pack(),
            ),
            InlineKeyboardButton(
                text="30 Days",
                callback_data=CheckAliveCBData(
                    filter_=CheckAliveCBFilter.DAYS_30
                ).pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="7 Days",
                callback_data=CheckAliveCBData(
                    filter_=CheckAliveCBFilter.DAYS_7
                ).pack(),
            ),
            InlineKeyboardButton(
                text="1 Day",
                callback_data=CheckAliveCBData(
                    filter_=CheckAliveCBFilter.DAYS_1
                ).pack(),
            ),
        ],
        [
            InlineKeyboardButton(text="Back", callback_data="admin:back_to_stats"),
        ],
    ],
)


@router.callback_query(StatsCBData.filter(F.action == StatsCBAction.CHECK_ALIVE))
async def cb_check_alive_from_stats(callback: CallbackQuery) -> None:
    """Redirect to check alive menu from stats."""
    if not (message := await process_inaccessible_message(callback)):
        return

    await callback.answer()

    await message.edit_text(
        "Select users to check:",
        reply_markup=check_alive_keyboard,
    )


@router.callback_query(F.data == "admin:back_to_stats")
@inject
async def cb_back_to_stats(
    callback: CallbackQuery,
    hub: FromDishka[TranslatorHub],
    interactor: FromDishka[GetStatsInteractor],
) -> None:
    """Return to stats view."""
    if not (message := await process_inaccessible_message(callback)):
        return

    locale = extract_language_code(callback.from_user.language_code)
    i18n = hub.get_translator_by_locale(locale)

    stats = await interactor()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("stats-top-inviters-btn"),
                    callback_data=StatsCBData(
                        action=StatsCBAction.TOP_REFERRERS
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="Check Alive",
                    callback_data=StatsCBData(action=StatsCBAction.CHECK_ALIVE).pack(),
                ),
            ]
        ]
    )

    await message.edit_text(
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
    await callback.answer()
