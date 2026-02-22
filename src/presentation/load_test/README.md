# Load Test CLI

A command-line tool for load testing the Telegram bot by feeding fake Telegram Update objects through the real Dispatcher stack. This exercises the complete request lifecycle: middleware, routers, handlers, interactors, and database operations.

## Overview

The load test CLI simulates Telegram updates without making actual API calls. It uses a `NoOpSession` that intercepts all outbound Telegram API requests and returns valid mock responses. This allows testing the full application stack under load:

```
CLI → Update Factory → Dispatcher.feed_update() → Middleware → Router → Handler → Interactor → DB
```

Key features:

- Tests the real bot stack: middleware, DI, handlers, interactors, database
- Concurrent request processing with configurable concurrency
- User pool management to simulate realistic traffic patterns
- Comprehensive metrics: throughput, latency percentiles, error tracking
- Extensible handler registry with auto-discovery
- Detailed reports saved to disk

## Prerequisites

The development database must be running with migrations applied:

```bash
# Start dev database
just up

# Run migrations
alembic upgrade head
```

The load test uses your `config.yaml` settings to connect to the database and initialize the bot stack.

## Usage

The CLI can run in two modes:

### Interactive Mode

Run without flags to be prompted for all parameters:

```bash
python -m src.presentation.load_test
```

You will be prompted for:
- Total updates to process
- Concurrency level
- Handler to test
- Test name (optional, auto-generated if empty)

### Non-Interactive Mode

Provide all required flags:

```bash
python -m src.presentation.load_test \
  --total 10000 \
  --concurrency 100 \
  --handler start \
  --name "baseline_test"
```

## CLI Options

| Flag | Short | Description | Default | Required |
|------|-------|-------------|---------|----------|
| `--total` | `-t` | Total updates to process | - | Yes (or prompted) |
| `--concurrency` | `-c` | Number of concurrent coroutines | - | Yes (or prompted) |
| `--handler` | - | Handler to test (see Available Handlers) | - | Yes (or prompted) |
| `--name` | `-n` | Custom test name for the report | Auto-generated | No |
| `--user-pool-size` | - | Number of unique fake users | 10,000 | No |
| `--base-user-id` | - | Starting user ID for fake users | 900,000,000 | No |

### Auto-Generated Test Names

If you don't provide `--name`, the test name is generated as:

```
{handler}_tu={total_updates}_cnc={concurrency}
```

Example: `start_tu=10000_cnc=100`

## Usage Examples

### Basic Load Test

Test the `/start` command with 10,000 updates and 100 concurrent workers:

```bash
python -m src.presentation.load_test \
  --total 10000 \
  --concurrency 100 \
  --handler start
```

### High Concurrency Test

Test language callback handling with 50,000 updates and 500 concurrent workers:

```bash
python -m src.presentation.load_test \
  --total 50000 \
  --concurrency 500 \
  --handler callback_language \
  --name "callback_high_concurrency"
```

### Small User Pool

Test with only 100 unique users to stress user-level contention:

```bash
python -m src.presentation.load_test \
  --total 10000 \
  --concurrency 200 \
  --handler start \
  --user-pool-size 100 \
  --name "small_user_pool"
```

### Custom User ID Range

Test with a specific user ID range (useful for isolating test data):

```bash
python -m src.presentation.load_test \
  --total 5000 \
  --concurrency 50 \
  --handler start \
  --base-user-id 800000000 \
  --user-pool-size 1000
```

## Available Handlers

### `start`

Tests the `/start` command flow:
- User creation/upsert via `UserAndLocaleMiddleware`
- Command routing and handler execution
- Database write operations

**Update structure**: Message with `/start` text and bot_command entity

### `callback_language`

Tests the language selection callback flow:
- Callback query routing
- Language preference updates
- CallbackQuery answer operations

**Update structure**: CallbackQuery with `onboarding:en` data

## Adding a New Handler

Handlers are automatically discovered via the registry pattern. To add a new handler, create a new file in `handlers/` with a factory function decorated with `@register_handler`.

### Step-by-Step Guide

1. Create a new file in `handlers/` (e.g., `handlers/help.py`)
2. Import required aiogram types, shared factories, and the decorator
3. Write a factory function that returns an `Update`
4. Decorate with `@register_handler("your_handler_name")`

### Complete Example

Create `src/presentation/load_test/handlers/help.py`:

```python
from aiogram.types import Message, Update

from src.presentation.load_test.factories import make_fake_chat, make_fake_user
from src.presentation.load_test.handlers.registry import register_handler


@register_handler("help")
def make_help_update(update_id: int, user_id: int) -> Update:
    """Create an Update with /help command."""
    user = make_fake_user(user_id)
    chat = make_fake_chat(user_id)

    message = Message(
        message_id=update_id,
        date=0,
        chat=chat,
        from_user=user,
        text="/help",
        entities=[{"type": "bot_command", "offset": 0, "length": 5}],
    )
    return Update(update_id=update_id, message=message)
```

That's it! The handler is automatically registered and available:

```bash
python -m src.presentation.load_test --total 1000 --concurrency 50 --handler help
```

### Shared Factories

Use the following helper functions from `factories.py`:

- `make_fake_user(user_id: int) -> User` - Creates a fake User with consistent properties
- `make_fake_chat(chat_id: int) -> Chat` - Creates a private Chat

### Handler Protocol

Your factory function must match this signature:

```python
def handler_function(update_id: int, user_id: int) -> Update:
    ...
```

- `update_id`: Unique sequential update ID (starts at 1)
- `user_id`: User ID from the pool (rotates based on `user_pool_size`)

### No Registry Modifications Needed

The `handlers/__init__.py` module automatically discovers and imports all `.py` files in the `handlers/` directory (except `__init__.py` and `registry.py`). Your handler is registered as soon as you create the file.

## Reports

### Report Location

Reports are saved to:

```
src/presentation/load_test/reports/
```

### File Naming

Reports use the format:

```
{timestamp}_{test_name}.txt
```

Example: `2026-02-21_14-30-45_start_tu=10000_cnc=100.txt`

### Report Contents

Each report includes:

**Test Configuration**
- Handler name
- Concurrency level
- Wall clock time

**Throughput Metrics**
- Updates per second
- Total processed
- Success count
- Error count and percentage

**Latency Metrics**
- Average latency (milliseconds)
- p50 (median)
- p95
- p99
- Min/max latency

**Error Details** (if errors occurred)
- Error types with counts
- Full traceback of first error

### Sample Report

```
============================================================
  start_tu=10000_cnc=100
============================================================
  Handler:             start
  Concurrency:         100
  Wall time:           8.45s
  Throughput:          1183.4 updates/sec

  Total processed:     10000
  Success:             10000
  Errors:              0
  Error rate:          0.0%

  Avg latency:         84.2 ms
  p50:                 76.3 ms
  p95:                 142.1 ms
  p99:                 187.5 ms
  Min:                 12.4 ms
  Max:                 312.8 ms

============================================================
```

## Architecture

### Data Flow

1. **CLI** (`cli.py`) - Parses arguments, validates handler name, invokes runner
2. **Runner** (`runner.py`) - Sets up dispatcher with DI, creates semaphore for concurrency control
3. **Registry** (`handlers/registry.py`) - Retrieves registered update factory by name
4. **Factory** (`handlers/*.py`) - Generates fake Update objects with sequential IDs and pooled user IDs
5. **Dispatcher** - Feeds updates through the real bot stack:
   - `UserAndLocaleMiddleware` - Creates/loads user from DB
   - Router - Matches command/callback pattern
   - Handler - Executes business logic
   - Interactor - Applies domain logic, writes to DB
6. **NoOpSession** (`session.py`) - Intercepts Telegram API calls, returns mock responses
7. **Metrics** (`metrics.py`) - Records latency and errors per update
8. **Report** (`report.py`) - Formats and saves metrics to disk

### Key Components

**NoOpSession**

A fake `BaseSession` implementation that intercepts all Telegram API method calls. Returns valid aiogram type instances to prevent deserialization errors:

- `SendMessage`, `EditMessageText`, `EditMessageReplyMarkup` → Returns mock `Message`
- `AnswerCallbackQuery`, `DeleteMessage` → Returns `True`
- Other methods → Returns `True`

This allows the bot to execute normally without making network requests.

**Update Factory Pattern**

Each handler is a factory function that generates an `Update` object. Factories are registered by name using the `@register_handler` decorator. This pattern enables:

- Clean separation between update generation and processing
- Easy addition of new test scenarios
- Consistent interface across all handlers

**User Pool**

User IDs are cycled from a pool to simulate realistic traffic:

```python
user_id = base_user_id + (update_index % user_pool_size)
```

Default pool: 10,000 users starting at ID 900,000,000. This prevents every update from being a new user while maintaining reasonable database diversity.

**Concurrency Control**

Uses `asyncio.Semaphore` to limit concurrent tasks. All updates are created upfront and processed via `asyncio.gather()`, ensuring fair scheduling and accurate wall time measurement.

## Troubleshooting

### Database Connection Errors

Ensure the dev database is running:

```bash
just up
alembic upgrade head
```

### Handler Not Found

List available handlers:

```bash
python -m src.presentation.load_test --help
```

Check that your handler file is in `handlers/` and uses the `@register_handler` decorator.

### High Error Rates

Check the first error traceback in the report. Common issues:

- Database connection pool exhaustion (increase pool size in `config.yaml`)
- Missing database tables (run migrations)
- Bot token issues (check `config.yaml`)

### Low Throughput

- Increase concurrency: `--concurrency 200`
- Check database performance (indexes, query plans)
- Profile slow interactors

### Memory Issues

For very large tests (100,000+ updates):

- Reduce `--user-pool-size` to limit in-memory user data
- Process in multiple smaller batches
- Monitor database connection pool usage