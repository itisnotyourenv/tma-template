import asyncio
import logging

import typer

from src.presentation.load_test.handlers import available_handlers
from src.presentation.load_test.runner import run_load_test

app = typer.Typer(
    help="Bot load testing - feeds fake Updates through the real Dispatcher stack.",
)


@app.command()
def run(
    total_updates: int = typer.Option(
        ...,
        "--total",
        "-t",
        prompt="Total updates",
        help="Total updates to process",
    ),
    concurrency: int = typer.Option(
        ...,
        "--concurrency",
        "-c",
        prompt="Concurrency",
        help="Concurrent coroutines",
    ),
    handler: str = typer.Option(
        ...,
        "--handler",
        prompt=f"Handler ({', '.join(available_handlers())})",
        help="Handler to test",
    ),
    test_name: str = typer.Option(
        "",
        "--name",
        "-n",
        prompt="Test name (enter to auto-generate)",
        prompt_required=False,
        help="Test name for the report",
    ),
    user_pool_size: int = typer.Option(
        10_000, "--user-pool-size", help="Number of unique fake users"
    ),
    base_user_id: int = typer.Option(
        900_000_000, "--base-user-id", help="Starting user ID"
    ),
) -> None:
    """Run a load test against a bot handler."""
    available = available_handlers()
    if handler not in available:
        typer.echo(f"Unknown handler '{handler}'. Available: {', '.join(available)}")
        raise typer.Exit(code=1)

    if not test_name:
        test_name = f"{handler}_tu={total_updates}_cnc={concurrency}"

    logging.basicConfig(level=logging.INFO)
    asyncio.run(
        run_load_test(
            total_updates=total_updates,
            concurrency=concurrency,
            handler=handler,
            test_name=test_name,
            user_pool_size=user_pool_size,
            base_user_id=base_user_id,
        )
    )
