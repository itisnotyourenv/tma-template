# ruff: noqa: RUF001 RUF002 RUF003 ASYNC109 PLC0415
"""
Нагрузочное тестирование бота через подачу фейковых Update в Dispatcher.

Тестирует полный стек: middleware → router → handler → interactor → DB.

Запуск:
    uv run python load_tests/bot_load_test.py \
        --total-updates 1000 \
        --concurrency 50 \
        --handler start

Параметры:
    --total-updates  Общее количество Update для обработки
    --concurrency    Кол-во одновременных задач (корутин)
    --handler        Какой хендлер тестировать: start | callback_language
"""

import argparse
import asyncio
import logging
import time
import traceback
from collections import defaultdict
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.base import BaseSession
from aiogram.enums import ParseMode
from aiogram.methods import TelegramMethod
from aiogram.methods.base import TelegramType
from aiogram.types import CallbackQuery, Chat, Message, Update, User
from dishka import make_async_container
from dishka.integrations.aiogram import setup_dishka

from src.infrastructure.config import Config, load_config
from src.infrastructure.di import (
    AuthProvider,
    DBProvider,
    I18nProvider,
    interactor_providers,
)
from src.presentation.bot.middleware.user_and_locale import UserAndLocaleMiddleware
from src.presentation.bot.routers import setup_routers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# No-op сессия — перехватывает все вызовы к Telegram API
# ---------------------------------------------------------------------------


class NoOpSession(BaseSession):
    """
    Фейковая сессия, которая не отправляет запросы в Telegram.
    Возвращает корректные объекты, чтобы aiogram не падал при десериализации.
    """

    async def make_request(
        self,
        bot: Bot,
        method: TelegramMethod[TelegramType],
        timeout: int | None = None,
    ) -> TelegramType | None:
        from aiogram.methods import (
            AnswerCallbackQuery,
            DeleteMessage,
            EditMessageReplyMarkup,
            EditMessageText,
            SendMessage,
        )

        if isinstance(method, AnswerCallbackQuery | DeleteMessage):
            return True

        if isinstance(method, SendMessage | EditMessageText | EditMessageReplyMarkup):
            return Message(
                message_id=1,
                date=0,
                chat=Chat(id=0, type="private"),
            )

        return True

    async def close(self) -> None:
        pass

    async def stream_content(
        self,
        url: str,
        headers: dict[str, Any] | None = None,
        timeout: int = 30,
        chunk_size: int = 65536,
        raise_for_status: bool = True,
    ) -> AsyncGenerator[bytes]:  # pragma: no cover
        """
        Stream reader
        """
        yield b""


# ---------------------------------------------------------------------------
# Фабрики для фейковых Telegram-объектов
# ---------------------------------------------------------------------------


def make_fake_user(user_id: int) -> User:
    return User(
        id=user_id,
        is_bot=False,
        first_name=f"LoadTestUser_{user_id}",
        language_code="en",
    )


def make_fake_chat(chat_id: int) -> Chat:
    return Chat(id=chat_id, type="private")


def make_start_update(update_id: int, user_id: int) -> Update:
    """Создаёт Update с командой /start."""
    user = make_fake_user(user_id)
    chat = make_fake_chat(user_id)

    message = Message(
        message_id=update_id,
        date=0,
        chat=chat,
        from_user=user,
        text="/start",
        entities=[
            {
                "type": "bot_command",
                "offset": 0,
                "length": 6,
            }
        ],
    )
    return Update(update_id=update_id, message=message)


def make_callback_update(update_id: int, user_id: int, data: str) -> Update:
    """Создаёт Update с CallbackQuery (например, выбор языка)."""
    user = make_fake_user(user_id)
    chat = make_fake_chat(user_id)

    message = Message(
        message_id=update_id - 1,
        date=0,
        chat=chat,
        from_user=user,
        text="Choose language:",
    )
    callback = CallbackQuery(
        id=str(update_id),
        chat_instance=str(user_id),
        from_user=user,
        message=message,
        data=data,
    )
    return Update(update_id=update_id, callback_query=callback)


# ---------------------------------------------------------------------------
# Сбор метрик
# ---------------------------------------------------------------------------


@dataclass
class LoadTestMetrics:
    total: int = 0
    success: int = 0
    errors: int = 0
    latencies: list[float] = field(default_factory=list)
    error_types: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    first_error: Exception | None = None
    first_error_tb: str | None = None

    def record_success(self, latency: float) -> None:
        self.total += 1
        self.success += 1
        self.latencies.append(latency)

    def record_error(self, error: Exception, latency: float) -> None:
        self.total += 1
        self.errors += 1
        self.latencies.append(latency)
        self.error_types[f"{type(error).__name__}: {error!s:.80}"] += 1
        if self.first_error is None:
            self.first_error = error
            self.first_error_tb = traceback.format_exc()

    def report(self) -> str:
        if not self.latencies:
            return "Нет данных."

        sorted_lat = sorted(self.latencies)
        p50 = sorted_lat[len(sorted_lat) // 2]
        p95 = sorted_lat[int(len(sorted_lat) * 0.95)]
        p99 = sorted_lat[int(len(sorted_lat) * 0.99)]
        total_time = sum(self.latencies)
        avg = total_time / len(self.latencies)
        rps = self.total / (max(sorted_lat) if sorted_lat else 1)

        lines = [
            "",
            "=" * 60,
            "  РЕЗУЛЬТАТЫ НАГРУЗОЧНОГО ТЕСТИРОВАНИЯ БОТА",
            "=" * 60,
            f"  Всего обработано:    {self.total}",
            f"  Успешно:             {self.success}",
            f"  Ошибок:              {self.errors}",
            f"  Error rate:          {self.errors / self.total * 100:.1f}%",
            f"  RPS:                 {rps:.1f}",
            "",
            f"  Avg latency:         {avg * 1000:.1f} ms",
            f"  p50:                 {p50 * 1000:.1f} ms",
            f"  p95:                 {p95 * 1000:.1f} ms",
            f"  p99:                 {p99 * 1000:.1f} ms",
            f"  Min:                 {sorted_lat[0] * 1000:.1f} ms",
            f"  Max:                 {sorted_lat[-1] * 1000:.1f} ms",
            "",
        ]

        if self.error_types:
            lines.append("  Типы ошибок:")
            for err_type, count in self.error_types.items():
                lines.append(f"    {err_type}: {count}")

        if self.first_error_tb:
            lines.append("")
            lines.append("  Первая ошибка (полный traceback):")
            lines.append("  " + "-" * 40)
            for line in self.first_error_tb.strip().splitlines():
                lines.append(f"  {line}")
            lines.append("  " + "-" * 40)

        lines.append("=" * 60)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Основная логика
# ---------------------------------------------------------------------------


async def setup_dispatcher(config: Config) -> tuple[Dispatcher, Bot]:
    """Инициализация Dispatcher с DI-контейнером (как в main.py)."""

    bot = Bot(
        token=config.telegram.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=NoOpSession(),  # Перехватываем ВСЕ вызовы к Telegram API
    )

    interactor_provider_instances = [
        interactor() for interactor in interactor_providers
    ]

    dp = Dispatcher()
    main_router = setup_routers()
    dp.include_router(main_router)

    container = make_async_container(
        AuthProvider(),
        DBProvider(config.postgres),
        I18nProvider(),
        *interactor_provider_instances,
        context={Config: config},
    )
    setup_dishka(container=container, router=dp)

    # Middleware
    dp.message.middleware(UserAndLocaleMiddleware())
    dp.callback_query.middleware(UserAndLocaleMiddleware())

    return dp, bot


async def process_single_update(
    dp: Dispatcher,
    bot: Bot,
    update: Update,
    metrics: LoadTestMetrics,
    semaphore: asyncio.Semaphore,
) -> None:
    """Обрабатывает один Update и записывает метрики."""
    async with semaphore:
        start = time.perf_counter()
        try:
            await dp.feed_update(bot=bot, update=update)

            elapsed = time.perf_counter() - start
            metrics.record_success(elapsed)
        except Exception as e:
            elapsed = time.perf_counter() - start
            metrics.record_error(e, elapsed)
            logger.error("Update %s failed: %s", update.update_id, e)


async def run_load_test(
    total_updates: int,
    concurrency: int,
    handler: str,
) -> None:
    config = load_config()
    dp, bot = await setup_dispatcher(config)
    metrics = LoadTestMetrics()
    semaphore = asyncio.Semaphore(concurrency)

    # Генерируем Update'ы
    updates: list[Update] = []
    base_user_id = 900_000_000  # Фейковые ID, чтобы не конфликтовать

    for i in range(total_updates):
        user_id = base_user_id + (i % 10_000)  # Пул из 10k юзеров
        update_id = i + 1

        if handler == "start":
            updates.append(make_start_update(update_id, user_id))
        elif handler == "callback_language":
            updates.append(make_callback_update(update_id, user_id, "onboarding:en"))
        else:
            raise ValueError(f"Unknown handler: {handler}")

    print(
        f"\n🚀 Запуск: {total_updates} updates, concurrency={concurrency}, handler={handler}"
    )
    wall_start = time.perf_counter()

    # Запускаем все корутины
    tasks = [
        process_single_update(dp, bot, update, metrics, semaphore) for update in updates
    ]
    await asyncio.gather(*tasks)

    wall_elapsed = time.perf_counter() - wall_start
    print(f"⏱  Wall time: {wall_elapsed:.2f}s")
    print(f"📊 Throughput: {total_updates / wall_elapsed:.1f} updates/sec")
    print(metrics.report())


def main() -> None:
    parser = argparse.ArgumentParser(description="Bot load testing")
    parser.add_argument("--total-updates", type=int, default=1000)
    parser.add_argument("--concurrency", type=int, default=50)
    parser.add_argument(
        "--handler",
        choices=["start", "callback_language"],
        default="start",
    )
    args = parser.parse_args()

    asyncio.run(
        run_load_test(
            total_updates=args.total_updates,
            concurrency=args.concurrency,
            handler=args.handler,
        )
    )


if __name__ == "__main__":
    main()
