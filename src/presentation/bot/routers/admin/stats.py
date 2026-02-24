import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    Message,
)
from dishka.integrations.aiogram import FromDishka, inject

from src.application.referral.stats import GetStatsInteractor, GetTopReferrersInteractor
from src.infrastructure.i18n import TranslatorRunner
from src.presentation.bot.utils.markups.admin import stats_main_markup

logger = logging.getLogger(__name__)

router = Router(name="admin_stats")


@router.message(Command("stats"))
@router.callback_query(F.data == "admin:back_to_stats")
@inject
async def stats_handler(
    update: Message | CallbackQuery,
    i18n: TranslatorRunner,
    interactor: FromDishka[GetStatsInteractor],
) -> None:
    """Handle /stats admin command."""
    logger.info("Admin %s requested stats", update.from_user.id)
    stats = await interactor()

    kwargs = {
        "text": i18n.stats_overview(
            total=stats.total_users,
            referred=stats.referred_count,
            referred_pct=stats.referred_percent,
            organic=stats.organic_count,
            organic_pct=stats.organic_percent,
        ),
        "reply_markup": stats_main_markup(i18n),
    }

    if isinstance(update, CallbackQuery):
        await update.message.edit_text(**kwargs)
    else:
        await update.answer(**kwargs)


@router.callback_query(F.data == "ref_top")
@inject
async def ref_top_callback(
    callback: CallbackQuery,
    i18n: TranslatorRunner,
    interactor: FromDishka[GetTopReferrersInteractor],
) -> None:
    """Handle top referrers callback."""
    logger.info("Admin %s requested top referrers", callback.from_user.id)

    limit = 10
    top = await interactor(limit)

    if not top:
        await callback.message.edit_text(text=i18n.stats_no_inviters())
        await callback.answer()
        return

    text = i18n.stats_top_inviters_header(limit=limit) + "\n\n"
    for i, ref in enumerate(top, 1):
        name = f"@{ref.username}" if ref.username else ref.first_name
        text += f"{i}. {name} — {ref.count}\n"

    await callback.message.edit_text(text=text)
    await callback.answer()
