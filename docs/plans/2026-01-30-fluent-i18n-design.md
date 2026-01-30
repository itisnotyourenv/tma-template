# Fluent i18n Integration Design

## Overview

Integrate fluentogram-based internationalization system, adapted from [quran_bot PR #4](https://github.com/itisnotyourenv/quran_bot/pull/4).

## Configuration

- **Supported languages:** English (`en`), Russian (`ru`)
- **Default/fallback language:** English
- **Language detection:** Telegram `language_code` only (no DB storage)
- **Locale file organization:** Feature-based files

## Infrastructure Module

**Location:** `src/infrastructure/i18n/`

```
src/infrastructure/i18n/
├── __init__.py      # Public exports
├── hub.py           # TranslatorHub factory
├── provider.py      # Dishka I18nProvider
└── stubs.pyi        # Auto-generated type stubs
```

**Dependencies:**
```
fluentogram>=0.4.0
fluent-compiler>=0.4.0
```

### hub.py

- Creates `TranslatorHub` that loads all `.ftl` files for each language
- Language fallback chain: `user's telegram language → English (default)`
- Supported languages constant: `("en", "ru")` with `"en"` as root

### provider.py

- Dishka `I18nProvider` provides `TranslatorHub` as app-scoped singleton
- Accepts optional `locale_dir` parameter (defaults to project root `/locales`)

## Locale Files

**Location:** `locales/`

```
locales/
├── en/
│   ├── common.ftl    # Shared strings (buttons, errors)
│   ├── start.ftl     # /start command messages
│   └── admin.ftl     # Admin-only messages
└── ru/
    ├── common.ftl
    ├── start.ftl
    └── admin.ftl
```

### Translation Keys

**start.ftl:**
```ftl
welcome = Hello, { $name }!
```

**admin.ftl:**
```ftl
example-executed = Example admin command executed
bot-started = Bot has started!
```

**common.ftl:**
```ftl
# Reserved for future shared strings
```

### Naming Convention

- Keys use `kebab-case` (Fluent standard)
- Files named after features they serve
- Parameters use `$param` syntax: `{ $name }`

## Handler Integration

Handlers inject `TranslatorHub` via Dishka and get translator for user's language:

```python
from fluentogram import TranslatorHub

@router.message(CommandStart())
@inject
async def command_start_handler(
    message: Message,
    interactor: FromDishka[CreateUserInteractor],
    hub: FromDishka[TranslatorHub],
) -> None:
    lang = message.from_user.language_code or "en"
    i18n = hub.get_translator_by_locale(lang[:2])

    user = await interactor(...)
    await message.answer(text=i18n.welcome(name=user.first_name))
```

### Files to Modify

| File | Changes |
|------|---------|
| `routers/commands.py` | Inject `TranslatorHub`, use `i18n.welcome()` |
| `routers/admin/example.py` | Inject `TranslatorHub`, use `i18n.example_executed()` |
| `main.py` | Add `I18nProvider` to container, use `i18n.bot_started()` |

## Stub Generator

**Location:** `scripts/generate_i18n_stubs.py`

Parses `.ftl` files and generates `stubs.pyi` for IDE autocomplete:

1. Reads all `.ftl` files from `locales/en/` (English as reference)
2. Extracts translation keys and their `{ $param }` parameters
3. Generates `TranslatorRunner` class with typed methods
4. Writes to `src/infrastructure/i18n/stubs.pyi`

**Generated output:**
```python
class TranslatorRunner:
    def welcome(self, *, name: str | int) -> str: ...
    def example_executed(self) -> str: ...
    def bot_started(self) -> str: ...
```

**Usage:**
```bash
python scripts/generate_i18n_stubs.py
```

## DI Integration

### src/infrastructure/di/__init__.py

Add `I18nProvider` to exports and `infra_providers` list.

### src/presentation/bot/main.py

Add `I18nProvider()` to container:

```python
container = make_async_container(
    AuthProvider(),
    DBProvider(config.postgres),
    I18nProvider(),
    *interactor_provider_instances,
    context={Config: config},
)
```

Update admin notification to use translator:

```python
async def notify_admins_on_startup(
    bot: Bot,
    config: Config,
    hub: TranslatorHub,
) -> None:
    i18n = hub.get_translator_by_locale("en")
    for admin_id in config.telegram.admin_ids:
        await bot.send_message(chat_id=admin_id, text=i18n.bot_started())
```

## File Summary

### New Files

| File | Purpose |
|------|---------|
| `src/infrastructure/i18n/__init__.py` | Module exports |
| `src/infrastructure/i18n/hub.py` | TranslatorHub factory |
| `src/infrastructure/i18n/provider.py` | Dishka provider |
| `src/infrastructure/i18n/stubs.pyi` | Type stubs (generated) |
| `scripts/generate_i18n_stubs.py` | Stub generator |
| `locales/en/common.ftl` | English common strings |
| `locales/en/start.ftl` | English start strings |
| `locales/en/admin.ftl` | English admin strings |
| `locales/ru/common.ftl` | Russian common strings |
| `locales/ru/start.ftl` | Russian start strings |
| `locales/ru/admin.ftl` | Russian admin strings |

### Modified Files

| File | Changes |
|------|---------|
| `pyproject.toml` | Add fluentogram, fluent-compiler |
| `src/infrastructure/di/__init__.py` | Export I18nProvider |
| `src/presentation/bot/main.py` | Add I18nProvider, update notify_admins |
| `src/presentation/bot/routers/commands.py` | Use i18n for welcome message |
| `src/presentation/bot/routers/admin/example.py` | Use i18n for admin message |
