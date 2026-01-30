# Referral System Design

## Overview

Реферальная система для отслеживания кто кого пригласил в бот. Только для внутренней аналитики — без UI для пользователей.

## Requirements

- **Цель**: Аналитика — отслеживать кто кого привёл
- **Реферальный код**: Зашифрованный User ID (обратимое шифрование)
- **UI для пользователей**: Нет
- **Просмотр статистики**: Админ-команды в боте
- **Данные для админов**: Общая статистика + топ рефереров
- **Определение админов**: Существующий `admin_ids` из конфига
- **Невалидный реферер**: Игнорируется, пользователь регистрируется без реферера

## Data Model

### User Entity Changes

```python
# src/domain/user/entity.py
@dataclass
class User:
    id: UserId
    first_name: FirstName
    last_name: LastName | None
    username: Username | None
    bio: Bio | None
    referred_by: UserId | None  # NEW: ID пригласившего
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime
```

### Database Migration

```sql
ALTER TABLE users ADD COLUMN referred_by BIGINT REFERENCES users(id) ON DELETE RESTRICT;
CREATE INDEX ix_users_referred_by ON users(referred_by);
```

- `ON DELETE RESTRICT` — нельзя удалить пользователя, у которого есть рефералы
- Индекс для быстрых запросов топа рефереров

Миграция генерируется автоматически: `alembic revision --autogenerate -m "add_referral_system"`

## Referral Code Encoding

XOR-шифрование с ключом из `auth.secret_key`. Использует только стандартную библиотеку Python.

```python
# src/domain/user/services/referral.py
import hashlib
import struct
import base64

def encode_referral(user_id: int, secret_key: str) -> str:
    """Шифрует user_id в короткий код"""
    key_hash = hashlib.sha256(secret_key.encode()).digest()
    key_int = int.from_bytes(key_hash[:8], "big")

    encrypted = user_id ^ key_int
    packed = struct.pack(">Q", encrypted)
    return base64.urlsafe_b64encode(packed).decode().rstrip("=")

def decode_referral(code: str, secret_key: str) -> int | None:
    """Расшифровывает код обратно в user_id"""
    try:
        padding = 4 - len(code) % 4
        if padding != 4:
            code += "=" * padding

        packed = base64.urlsafe_b64decode(code)
        encrypted = struct.unpack(">Q", packed)[0]

        key_hash = hashlib.sha256(secret_key.encode()).digest()
        key_int = int.from_bytes(key_hash[:8], "big")

        return encrypted ^ key_int
    except Exception:
        return None
```

**Deep link формат**: `t.me/bot_name?start=ref_<code>`

## Application Layer

### CreateUserInteractor Changes

Валидация реферера происходит в интеракторе (бизнес-логика):

```python
# src/application/user/create.py
class CreateUserInteractor:
    async def __call__(self, data: CreateUserInputDTO) -> CreateUserOutputDTO:
        validated_referrer_id = None
        if data.referred_by:
            referrer = await self.user_repository.get_user(UserId(data.referred_by))
            if referrer:
                validated_referrer_id = data.referred_by

        user = await self.user_service.upsert_user(
            UpsertUserData(..., referred_by=validated_referrer_id)
        )
        ...
```

### New Interactors

```python
# src/application/user/stats.py

@dataclass
class StatsOutputDTO:
    total_users: int
    referred_count: int
    referred_percent: float
    organic_count: int
    organic_percent: float

@dataclass
class TopReferrerDTO:
    user_id: int
    username: str | None
    first_name: str
    count: int

class GetStatsInteractor:
    async def __call__(self) -> StatsOutputDTO: ...

class GetTopReferrersInteractor:
    async def __call__(self, limit: int = 10) -> list[TopReferrerDTO]: ...
```

## Presentation Layer

### Bot Handler Changes

```python
# src/presentation/bot/routers/commands.py
@router.message(CommandStart(deep_link=True))
async def command_start_handler(message: Message, command: CommandObject, ...):
    referred_by_id = None

    if command.args and command.args.startswith("ref_"):
        code = command.args[4:]
        referred_by_id = decode_referral(code, secret_key)

    user = await create_user_interactor(
        CreateUserInputDTO(..., referred_by=referred_by_id)
    )
```

### Admin Commands

Переименовать `example.py` → `stats.py`:

```python
# src/presentation/bot/routers/admin/stats.py

@router.message(Command("stats"))
@inject
async def stats_handler(
    message: Message,
    hub: FromDishka[TranslatorHub],
    interactor: FromDishka[GetStatsInteractor],
):
    locale = extract_language_code(message.from_user.language_code)
    i18n = hub.get_translator_by_locale(locale)

    stats = await interactor()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=i18n.get("stats-top-inviters-btn"),
            callback_data="ref_top"
        )]
    ])

    await message.answer(
        text=i18n.get("stats-overview", ...),
        reply_markup=keyboard
    )

@router.callback_query(F.data == "ref_top")
@inject
async def ref_top_callback(callback: CallbackQuery, ...):
    top = await get_top_referrers_interactor(limit=10)
    text = i18n.get("stats-top-inviters", limit=10)
    for i, ref in enumerate(top, 1):
        name = f"@{ref.username}" if ref.username else ref.first_name
        text += f"\n{i}. {name} — {ref.count}"

    await callback.message.edit_text(text)
```

## Localization

```ftl
# locales/ru/bot.ftl
stats-overview = 📊 Статистика

    Всего: { $total }
    По рефералам: { $referred } ({ $referred_pct }%)
    Органика: { $organic } ({ $organic_pct }%)

stats-top-inviters-btn = 🏆 Топ инвайтеров

stats-top-inviters = 🏆 Топ-{ $limit } инвайтеров:
```

```ftl
# locales/en/bot.ftl
stats-overview = 📊 Statistics

    Total: { $total }
    Referred: { $referred } ({ $referred_pct }%)
    Organic: { $organic } ({ $organic_pct }%)

stats-top-inviters-btn = 🏆 Top inviters

stats-top-inviters = 🏆 Top { $limit } inviters:
```

## File Structure

```
src/
├── domain/user/
│   ├── vo.py                    # (без изменений)
│   ├── entity.py                # + referred_by: UserId | None
│   └── services/
│       └── referral.py          # encode/decode (NEW)
│
├── application/user/
│   ├── create.py                # + валидация реферера
│   ├── dto.py                   # + referred_by в DTO
│   └── stats.py                 # GetStatsInteractor, GetTopReferrersInteractor (NEW)
│
├── infrastructure/
│   ├── db/
│   │   ├── models/user.py       # + referred_by колонка
│   │   ├── repos/user.py        # + методы для статистики
│   │   └── migrations/versions/ # + миграция (autogenerate)
│   └── di/                      # + провайдеры для новых интеракторов
│
├── presentation/bot/
│   └── routers/
│       ├── commands.py          # + парсинг ref_ из deep link
│       └── admin/
│           └── stats.py         # /stats + callback (NEW, replace example.py)
│
└── locales/
    ├── ru/bot.ftl               # + ключи статистики
    └── en/bot.ftl               # + ключи статистики
```

## Summary

| Аспект | Решение |
|--------|---------|
| **Цель** | Аналитика — кто кого пригласил |
| **Хранение** | Поле `referred_by` в таблице `users` |
| **Реферальный код** | XOR-шифрование user_id (stdlib) |
| **Deep link** | `t.me/bot?start=ref_<code>` |
| **Невалидный реферер** | Игнорируется в интеракторе |
| **FK constraint** | `ON DELETE RESTRICT` |
| **UI для пользователей** | Нет |
| **Админ-доступ** | Существующий `AdminFilter` |
| **Админ-команда** | `/stats` + inline-кнопка |
| **Локализация** | fluentogram (ru/en) |
