import asyncio
import logging
import time

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update
from dishka import make_async_container
from dishka.integrations.aiogram import setup_dishka
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from src.infrastructure.config import Config, load_config
from src.infrastructure.di import (
    AuthProvider,
    DBProvider,
    I18nProvider,
    interactor_providers,
)
from src.presentation.bot.middleware.user_and_locale import UserAndLocaleMiddleware
from src.presentation.bot.routers import setup_routers
from src.presentation.load_test.handlers import get_handler
from src.presentation.load_test.metrics import LoadTestMetrics
from src.presentation.load_test.report import format_report, print_report, save_report
from src.presentation.load_test.session import NoOpSession

logger = logging.getLogger(__name__)

# Suppress aiogram INFO logs during the test so the progress bar stays clean
aiogram_logger = logging.getLogger("aiogram.event")
aiogram_logger.setLevel(logging.WARNING)


async def setup_dispatcher(config: Config) -> tuple[Dispatcher, Bot]:
    """Initialize Dispatcher with DI container and NoOpSession."""
    bot = Bot(
        token=config.telegram.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=NoOpSession(),
    )

    interactor_provider_instances = [
        interactor() for interactor in interactor_providers
    ]

    dp = Dispatcher(config=config)
    main_router = setup_routers()
    dp.include_router(main_router)

    container = make_async_container(
        AuthProvider(),
        DBProvider(),
        I18nProvider(),
        *interactor_provider_instances,
        context={Config: config},
    )
    setup_dishka(container=container, router=dp)

    dp.message.middleware(UserAndLocaleMiddleware())
    dp.callback_query.middleware(UserAndLocaleMiddleware())

    return dp, bot


async def _process_single_update(
    dp: Dispatcher,
    bot: Bot,
    update: Update,
    metrics: LoadTestMetrics,
    semaphore: asyncio.Semaphore,
    progress: Progress,
    task_id,
) -> None:
    """Process a single Update and record metrics."""
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
        finally:
            progress.advance(task_id)


async def run_load_test(
    total_updates: int,
    concurrency: int,
    handler: str,
    test_name: str,
    user_pool_size: int,
    base_user_id: int,
) -> None:
    """Run the load test: generate updates, feed through dispatcher, report."""
    config = load_config()
    dp, bot = await setup_dispatcher(config)
    metrics = LoadTestMetrics()
    semaphore = asyncio.Semaphore(concurrency)

    factory = get_handler(handler)
    updates = [
        factory(
            update_id=i + 1,
            user_id=base_user_id + (i % user_pool_size),
        )
        for i in range(total_updates)
    ]

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        TaskProgressColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
    )

    with progress:
        task_id = progress.add_task(f"[{handler}]", total=total_updates)
        wall_start = time.perf_counter()

        tasks = [
            _process_single_update(
                dp, bot, update, metrics, semaphore, progress, task_id
            )
            for update in updates
        ]
        await asyncio.gather(*tasks)

    wall_elapsed = time.perf_counter() - wall_start

    # Rich output to console
    print_report(
        metrics=metrics,
        test_name=test_name,
        wall_elapsed=wall_elapsed,
        handler=handler,
        concurrency=concurrency,
    )

    # Plain text to file
    report_text = format_report(
        metrics=metrics,
        test_name=test_name,
        wall_elapsed=wall_elapsed,
        handler=handler,
        concurrency=concurrency,
    )
    filepath = save_report(report_text, test_name)

    from rich.console import Console

    Console().print(f"\nReport saved: [bold green]{filepath}[/bold green]")
