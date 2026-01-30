# Referral System Design

**Дата:** 2026-01-30
**Статус:** Утверждён

## Обзор

Реализация реферальной системы для отслеживания, кто кого пригласил в бота. Система включает:
- Хранение связи реферер → приглашённый
- Счётчик приглашённых пользователей
- Генерация реферальной ссылки на основе хеша ID
- Команда `/referral` для получения ссылки и статистики

## Требования

- **Цель:** отслеживание (аналитика), без системы вознаграждений
- **Ссылка:** хеш из ID пользователя (8 символов)
- **Хранение:** поле `referred_by` + счётчик `referral_count`
- **Интерфейс:** команда `/referral` в боте
- **Крайний случай:** реферал засчитывается только для новых пользователей

## Модель данных

### Изменения в модели User

Добавляем два поля в существующую модель пользователя:

```python
# domain/user/entity.py
@dataclass
class User:
    # ... существующие поля ...
    referred_by: UserId | None      # ID пользователя, который пригласил
    referral_count: int             # Количество приглашённых (по умолчанию 0)
```

### Миграция базы данных

```sql
ALTER TABLE users
    ADD COLUMN referred_by BIGINT REFERENCES users(id),
    ADD COLUMN referral_count INTEGER NOT NULL DEFAULT 0;
```

**Почему счётчик, а не COUNT запрос:**
- Мгновенный доступ без JOIN/подзапроса
- При больших объёмах COUNT по внешнему ключу дорогой
- Инкрементируется атомарно при регистрации нового реферала

## Генерация реферального кода

### Алгоритм хеширования

Используем детерминированный хеш из Telegram ID пользователя:

```python
# domain/user/services/referral.py
import hashlib

def generate_referral_code(user_id: int) -> str:
    """Генерирует 8-символьный код из user_id."""
    hash_input = f"referral:{user_id}".encode()
    hash_digest = hashlib.sha256(hash_input).hexdigest()
    return hash_digest[:8]  # Первые 8 символов

def decode_referral_code(code: str, all_user_ids: list[int]) -> int | None:
    """Находит user_id по коду (перебор существующих пользователей)."""
    for user_id in all_user_ids:
        if generate_referral_code(user_id) == code:
            return user_id
    return None
```

**Характеристики:**
- **Детерминированность** — не нужно хранить коды в БД
- **Соль "referral:"** — защита от простого перебора
- **8 символов** — 16^8 = 4 млрд комбинаций, достаточно для уникальности

### Формат ссылки

```
https://t.me/bot_username?start=ref_a1b2c3d4
```

Префикс `ref_` позволяет отличить реферальные ссылки от других `start_param`.

## Обработка реферальной ссылки

### Модификация /start хендлера

При старте бота проверяем `start_param` на наличие реферального кода:

```python
# presentation/bot/routers/commands.py
@router.message(CommandStart())
async def start_handler(
    message: Message,
    command: CommandObject,
    create_user: CreateUserInteractor,
    process_referral: ProcessReferralInteractor,
):
    user = message.from_user

    # Создаём/обновляем пользователя
    result = await create_user(...)
    is_new_user = result.is_new

    # Обрабатываем реферал только для новых пользователей
    if is_new_user and command.args and command.args.startswith("ref_"):
        referral_code = command.args[4:]  # Убираем "ref_"
        await process_referral(
            new_user_id=user.id,
            referral_code=referral_code,
        )

    await message.answer(f"Привет, {user.first_name}!")
```

### Логика ProcessReferralInteractor

1. Найти реферера по коду (decode_referral_code)
2. Проверить, что реферер существует и это не сам пользователь
3. Установить `referred_by` у нового пользователя
4. Инкрементировать `referral_count` у реферера

### Изменения в CreateUserInteractor

- Возвращать флаг `is_new` — был ли пользователь создан или обновлён

## Команда /referral

### Хендлер

```python
# presentation/bot/routers/referral.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="referral")

@router.message(Command("referral"))
async def referral_handler(
    message: Message,
    get_referral_info: GetReferralInfoInteractor,
    config: Config,
):
    user_id = message.from_user.id
    info = await get_referral_info(user_id)

    bot_username = config.telegram.bot_username
    referral_link = f"https://t.me/{bot_username}?start=ref_{info.referral_code}"

    text = (
        f"🔗 Ваша реферальная ссылка:\n"
        f"{referral_link}\n\n"
        f"👥 Приглашено пользователей: {info.referral_count}"
    )

    await message.answer(text)
```

### GetReferralInfoInteractor

- Получает пользователя из БД
- Генерирует реферальный код из ID
- Возвращает DTO с кодом и счётчиком

### Дополнение конфигурации

- Добавить `bot_username` в `config.telegram` для формирования ссылки

## Структура файлов

### Новые файлы

```
src/
├── domain/user/
│   └── services/
│       └── referral.py          # generate_referral_code, decode_referral_code
├── application/
│   └── referral/
│       ├── process.py           # ProcessReferralInteractor
│       └── get_info.py          # GetReferralInfoInteractor
├── presentation/bot/routers/
│   └── referral.py              # /referral хендлер
└── infrastructure/db/
    └── migrations/
        └── versions/
            └── xxx_add_referral_fields.py
```

### Изменяемые файлы

- `domain/user/entity.py` — добавить поля
- `domain/user/vo.py` — добавить ReferralCount value object (если нужно)
- `infrastructure/db/models/user.py` — добавить колонки
- `application/user/create.py` — возвращать `is_new`
- `presentation/bot/routers/commands.py` — обработка ref_ в /start
- `presentation/bot/main.py` — подключить referral router
- `infrastructure/config.py` — добавить bot_username
- `infrastructure/di/` — зарегистрировать новые интеракторы

## Тестирование

- Unit-тесты для `generate_referral_code` (детерминированность, длина)
- Unit-тесты для `decode_referral_code` (корректный поиск, not found)
- Integration-тест: полный флоу — создание реферера → переход по ссылке → проверка связи и счётчика