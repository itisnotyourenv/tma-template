# Referral System Updates Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Доработать существующую реферальную систему: заменить SHA256-хеш на XOR-шифрование с секретным ключом, добавить админ-команду /stats с inline-кнопкой для топа инвайтеров, добавить ON DELETE RESTRICT в миграцию, добавить i18n.

**Architecture:** XOR-шифрование user_id с ключом из `auth.secret_key`. Статистика через новые методы репозитория и интеракторы. Админ-команда /stats с callback-кнопкой.

**Tech Stack:** Python stdlib (hashlib, struct, base64), aiogram (InlineKeyboardMarkup, CallbackQuery), fluentogram (i18n)

---

## Task 1: Заменить хеширование на XOR-шифрование

**Files:**
- Modify: `src/domain/user/services/referral.py`
- Modify: `tests/unit/domain/user/services/test_referral.py`

**Step 1: Write the failing test**

Replace `tests/unit/domain/user/services/test_referral.py`:
```python
import pytest

from src.domain.user.services.referral import decode_referral, encode_referral


class TestReferralEncoding:
    def test_encode_decode_roundtrip(self) -> None:
        user_id = 123456789
        secret_key = "test-secret-key"

        code = encode_referral(user_id, secret_key)
        decoded = decode_referral(code, secret_key)

        assert decoded == user_id

    def test_encode_produces_url_safe_string(self) -> None:
        user_id = 987654321
        secret_key = "my-secret"

        code = encode_referral(user_id, secret_key)

        assert all(c.isalnum() or c in "-_" for c in code)

    def test_decode_with_wrong_key_returns_different_id(self) -> None:
        user_id = 123456789
        code = encode_referral(user_id, "correct-key")

        decoded = decode_referral(code, "wrong-key")

        assert decoded != user_id

    def test_decode_invalid_code_returns_none(self) -> None:
        result = decode_referral("invalid!", "any-key")

        assert result is None

    def test_different_users_get_different_codes(self) -> None:
        secret = "shared-secret"

        code1 = encode_referral(111, secret)
        code2 = encode_referral(222, secret)

        assert code1 != code2

    @pytest.mark.parametrize("user_id", [1, 100, 999999999, 9223372036854775807])
    def test_handles_various_user_ids(self, user_id: int) -> None:
        secret = "test-secret"
        code = encode_referral(user_id, secret)
        decoded = decode_referral(code, secret)
        assert decoded == user_id
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/domain/user/services/test_referral.py -v`
Expected: FAIL with "cannot import name 'encode_referral'"

**Step 3: Write implementation**

Replace `src/domain/user/services/referral.py`:
```python
import base64
import hashlib
import struct


def encode_referral(user_id: int, secret_key: str) -> str:
    """Encode user_id into a short referral code using XOR encryption."""
    key_hash = hashlib.sha256(secret_key.encode()).digest()
    key_int = int.from_bytes(key_hash[:8], "big")

    encrypted = user_id ^ key_int
    packed = struct.pack(">Q", encrypted)
    return base64.urlsafe_b64encode(packed).decode().rstrip("=")


def decode_referral(code: str, secret_key: str) -> int | None:
    """Decode referral code back to user_id. Returns None if invalid."""
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

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/domain/user/services/test_referral.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/domain/user/services/referral.py tests/unit/domain/user/services/test_referral.py
git commit -m "refactor(referral): replace SHA256 hash with XOR encryption

Use secret key from config for reversible encoding/decoding."
```

---

## Task 2: Обновить ProcessReferralInteractor

**Files:**
- Modify: `src/application/referral/process.py`
- Modify: `src/infrastructure/di/interactors/referral.py`
- Modify: `tests/unit/application/referral/test_process.py`

**Step 1: Update interactor**

Replace `src/application/referral/process.py`:
```python
from dataclasses import dataclass

from src.application.common.interactor import Interactor
from src.application.common.transaction import TransactionManager
from src.domain.user import UserRepository
from src.domain.user.services.referral import decode_referral
from src.domain.user.vo import UserId


@dataclass
class ProcessReferralInputDTO:
    new_user_id: int
    referral_code: str


class ProcessReferralInteractor(Interactor[ProcessReferralInputDTO, bool]):
    def __init__(
        self,
        user_repository: UserRepository,
        transaction_manager: TransactionManager,
        secret_key: str,
    ) -> None:
        self.user_repository = user_repository
        self.transaction_manager = transaction_manager
        self.secret_key = secret_key

    async def __call__(self, data: ProcessReferralInputDTO) -> bool:
        referrer_id = decode_referral(data.referral_code, self.secret_key)

        if referrer_id is None:
            return False

        if referrer_id == data.new_user_id:
            return False

        # Verify referrer exists
        referrer = await self.user_repository.get_user(UserId(referrer_id))
        if referrer is None:
            return False

        await self.user_repository.set_referred_by(
            UserId(data.new_user_id), UserId(referrer_id)
        )
        await self.user_repository.increment_referral_count(UserId(referrer_id))
        await self.transaction_manager.commit()

        return True
```

**Step 2: Update DI provider**

Replace `src/infrastructure/di/interactors/referral.py`:
```python
from dishka import Provider, Scope, provide

from src.application.common.transaction import TransactionManager
from src.application.referral.get_info import GetReferralInfoInteractor
from src.application.referral.process import ProcessReferralInteractor
from src.application.referral.stats import GetStatsInteractor, GetTopReferrersInteractor
from src.domain.user import UserRepository
from src.infrastructure.config import Config


class ReferralInteractorProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def provide_process_referral_interactor(
        self,
        user_repository: UserRepository,
        transaction_manager: TransactionManager,
        config: Config,
    ) -> ProcessReferralInteractor:
        return ProcessReferralInteractor(
            user_repository=user_repository,
            transaction_manager=transaction_manager,
            secret_key=config.auth.secret_key,
        )

    @provide
    def provide_get_referral_info_interactor(
        self,
        user_repository: UserRepository,
        config: Config,
    ) -> GetReferralInfoInteractor:
        return GetReferralInfoInteractor(
            user_repository=user_repository,
            secret_key=config.auth.secret_key,
        )

    @provide
    def provide_get_stats_interactor(
        self,
        user_repository: UserRepository,
    ) -> GetStatsInteractor:
        return GetStatsInteractor(user_repository=user_repository)

    @provide
    def provide_get_top_referrers_interactor(
        self,
        user_repository: UserRepository,
    ) -> GetTopReferrersInteractor:
        return GetTopReferrersInteractor(user_repository=user_repository)
```

**Step 3: Update tests**

Replace `tests/unit/application/referral/test_process.py`:
```python
from unittest.mock import AsyncMock, Mock

import pytest

from src.application.referral.process import (
    ProcessReferralInputDTO,
    ProcessReferralInteractor,
)
from src.domain.user.entity import User
from src.domain.user.services.referral import encode_referral


@pytest.fixture
def secret_key() -> str:
    return "test-secret-key"


@pytest.fixture
def user_repository() -> Mock:
    return Mock()


@pytest.fixture
def transaction_manager() -> Mock:
    manager = Mock()
    manager.commit = AsyncMock()
    return manager


@pytest.fixture
def interactor(
    user_repository: Mock,
    transaction_manager: Mock,
    secret_key: str,
) -> ProcessReferralInteractor:
    return ProcessReferralInteractor(
        user_repository=user_repository,
        transaction_manager=transaction_manager,
        secret_key=secret_key,
    )


class TestProcessReferralInteractor:
    async def test_valid_referral_sets_referred_by(
        self,
        interactor: ProcessReferralInteractor,
        user_repository: Mock,
        secret_key: str,
    ) -> None:
        referrer_id = 100
        new_user_id = 200
        code = encode_referral(referrer_id, secret_key)

        referrer = Mock(spec=User)
        user_repository.get_user = AsyncMock(return_value=referrer)
        user_repository.set_referred_by = AsyncMock()
        user_repository.increment_referral_count = AsyncMock()

        result = await interactor(
            ProcessReferralInputDTO(new_user_id=new_user_id, referral_code=code)
        )

        assert result is True
        user_repository.set_referred_by.assert_called_once()

    async def test_invalid_code_returns_false(
        self,
        interactor: ProcessReferralInteractor,
    ) -> None:
        result = await interactor(
            ProcessReferralInputDTO(new_user_id=200, referral_code="invalid!")
        )

        assert result is False

    async def test_self_referral_returns_false(
        self,
        interactor: ProcessReferralInteractor,
        secret_key: str,
    ) -> None:
        user_id = 100
        code = encode_referral(user_id, secret_key)

        result = await interactor(
            ProcessReferralInputDTO(new_user_id=user_id, referral_code=code)
        )

        assert result is False

    async def test_nonexistent_referrer_returns_false(
        self,
        interactor: ProcessReferralInteractor,
        user_repository: Mock,
        secret_key: str,
    ) -> None:
        code = encode_referral(100, secret_key)
        user_repository.get_user = AsyncMock(return_value=None)

        result = await interactor(
            ProcessReferralInputDTO(new_user_id=200, referral_code=code)
        )

        assert result is False
```

**Step 4: Run tests**

Run: `pytest tests/unit/application/referral/ -v`
Expected: Some tests may fail until stats interactors are created

**Step 5: Commit**

```bash
git add src/application/referral/process.py src/infrastructure/di/interactors/referral.py tests/unit/application/referral/test_process.py
git commit -m "refactor(referral): use decode_referral with secret key"
```

---

## Task 3: Обновить миграцию с ON DELETE RESTRICT и индексом

**Files:**
- Modify: `src/infrastructure/db/migrations/versions/2026_01_30_1200-7e29d6909fea_add_referral_fields.py`

**Step 1: Update migration**

Replace the `upgrade` function:
```python
def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column("referred_by", sa.BIGINT(), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column(
            "referral_count",
            sa.INTEGER(),
            server_default="0",
            nullable=False,
        ),
    )
    op.create_foreign_key(
        "fk_users_referred_by",
        "users",
        "users",
        ["referred_by"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_users_referred_by", "users", ["referred_by"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_users_referred_by", table_name="users")
    op.drop_constraint("fk_users_referred_by", "users", type_="foreignkey")
    op.drop_column("users", "referral_count")
    op.drop_column("users", "referred_by")
```

**Step 2: Commit**

```bash
git add src/infrastructure/db/migrations/versions/2026_01_30_1200-7e29d6909fea_add_referral_fields.py
git commit -m "fix(migration): add ON DELETE RESTRICT and index for referred_by"
```

---

## Task 4: Добавить методы статистики в репозиторий

**Files:**
- Modify: `src/domain/user/repository.py`
- Modify: `src/infrastructure/db/repos/user.py`

**Step 1: Add to protocol**

Add to `src/domain/user/repository.py`:
```python
from dataclasses import dataclass


@dataclass
class ReferralStats:
    total_users: int
    referred_count: int
    organic_count: int


@dataclass
class TopReferrer:
    user_id: int
    username: str | None
    first_name: str
    referral_count: int
```

And add methods to the `UserRepository` class:
```python
async def get_referral_stats(self) -> ReferralStats:
    """Get overall referral statistics."""
    ...

async def get_top_referrers(self, limit: int = 10) -> list[TopReferrer]:
    """Get top referrers by referral count."""
    ...
```

**Step 2: Implement in repository**

Add to `src/infrastructure/db/repos/user.py`:
```python
from src.domain.user.repository import ReferralStats, TopReferrer

async def get_referral_stats(self) -> ReferralStats:
    total_query = select(func.count()).select_from(UserModel)
    referred_query = select(func.count()).select_from(UserModel).where(
        UserModel.referred_by.isnot(None)
    )

    total = (await self._session.execute(total_query)).scalar() or 0
    referred = (await self._session.execute(referred_query)).scalar() or 0

    return ReferralStats(
        total_users=total,
        referred_count=referred,
        organic_count=total - referred,
    )

async def get_top_referrers(self, limit: int = 10) -> list[TopReferrer]:
    query = (
        select(UserModel)
        .where(UserModel.referral_count > 0)
        .order_by(UserModel.referral_count.desc())
        .limit(limit)
    )
    result = await self._session.execute(query)
    users = result.scalars().all()

    return [
        TopReferrer(
            user_id=int(u.id),
            username=str(u.username) if u.username else None,
            first_name=str(u.first_name),
            referral_count=int(u.referral_count),
        )
        for u in users
    ]
```

**Step 3: Commit**

```bash
git add src/domain/user/repository.py src/infrastructure/db/repos/user.py
git commit -m "feat(repo): add referral statistics methods"
```

---

## Task 5: Создать интеракторы статистики

**Files:**
- Create: `src/application/referral/stats.py`
- Create: `tests/unit/application/referral/test_stats.py`

**Step 1: Create stats interactors**

Create `src/application/referral/stats.py`:
```python
from dataclasses import dataclass

from src.application.common.interactor import Interactor
from src.domain.user import UserRepository


@dataclass
class StatsOutputDTO:
    total_users: int
    referred_count: int
    referred_percent: float
    organic_count: int
    organic_percent: float


class GetStatsInteractor(Interactor[None, StatsOutputDTO]):
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def __call__(self, data: None = None) -> StatsOutputDTO:
        stats = await self.user_repository.get_referral_stats()

        if stats.total_users > 0:
            referred_pct = stats.referred_count / stats.total_users * 100
            organic_pct = stats.organic_count / stats.total_users * 100
        else:
            referred_pct = 0
            organic_pct = 0

        return StatsOutputDTO(
            total_users=stats.total_users,
            referred_count=stats.referred_count,
            referred_percent=round(referred_pct, 1),
            organic_count=stats.organic_count,
            organic_percent=round(organic_pct, 1),
        )


@dataclass
class TopReferrerDTO:
    user_id: int
    username: str | None
    first_name: str
    count: int


class GetTopReferrersInteractor(Interactor[int, list[TopReferrerDTO]]):
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def __call__(self, data: int = 10) -> list[TopReferrerDTO]:
        top = await self.user_repository.get_top_referrers(limit=data)

        return [
            TopReferrerDTO(
                user_id=r.user_id,
                username=r.username,
                first_name=r.first_name,
                count=r.referral_count,
            )
            for r in top
        ]
```

**Step 2: Create tests**

Create `tests/unit/application/referral/test_stats.py`:
```python
from unittest.mock import AsyncMock, Mock

import pytest

from src.application.referral.stats import (
    GetStatsInteractor,
    GetTopReferrersInteractor,
    StatsOutputDTO,
    TopReferrerDTO,
)
from src.domain.user.repository import ReferralStats, TopReferrer


class TestGetStatsInteractor:
    @pytest.fixture
    def user_repository(self) -> Mock:
        return Mock()

    @pytest.fixture
    def interactor(self, user_repository: Mock) -> GetStatsInteractor:
        return GetStatsInteractor(user_repository=user_repository)

    async def test_returns_stats(
        self, interactor: GetStatsInteractor, user_repository: Mock
    ) -> None:
        user_repository.get_referral_stats = AsyncMock(
            return_value=ReferralStats(
                total_users=100,
                referred_count=40,
                organic_count=60,
            )
        )

        result = await interactor()

        assert isinstance(result, StatsOutputDTO)
        assert result.total_users == 100
        assert result.referred_count == 40
        assert result.referred_percent == 40.0
        assert result.organic_count == 60
        assert result.organic_percent == 60.0

    async def test_handles_zero_users(
        self, interactor: GetStatsInteractor, user_repository: Mock
    ) -> None:
        user_repository.get_referral_stats = AsyncMock(
            return_value=ReferralStats(
                total_users=0,
                referred_count=0,
                organic_count=0,
            )
        )

        result = await interactor()

        assert result.referred_percent == 0
        assert result.organic_percent == 0


class TestGetTopReferrersInteractor:
    @pytest.fixture
    def user_repository(self) -> Mock:
        return Mock()

    @pytest.fixture
    def interactor(self, user_repository: Mock) -> GetTopReferrersInteractor:
        return GetTopReferrersInteractor(user_repository=user_repository)

    async def test_returns_top_referrers(
        self, interactor: GetTopReferrersInteractor, user_repository: Mock
    ) -> None:
        user_repository.get_top_referrers = AsyncMock(
            return_value=[
                TopReferrer(user_id=1, username="user1", first_name="John", referral_count=10),
                TopReferrer(user_id=2, username=None, first_name="Jane", referral_count=5),
            ]
        )

        result = await interactor(10)

        assert len(result) == 2
        assert isinstance(result[0], TopReferrerDTO)
        assert result[0].count == 10
        assert result[1].username is None
```

**Step 3: Run tests**

Run: `pytest tests/unit/application/referral/test_stats.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add src/application/referral/stats.py tests/unit/application/referral/test_stats.py
git commit -m "feat(referral): add statistics interactors"
```

---

## Task 6: Обновить GetReferralInfoInteractor

**Files:**
- Modify: `src/application/referral/get_info.py`
- Modify: `tests/unit/application/referral/test_get_info.py`

**Step 1: Update interactor**

Replace `src/application/referral/get_info.py`:
```python
from dataclasses import dataclass

from src.application.common.interactor import Interactor
from src.domain.user import UserRepository
from src.domain.user.services.referral import encode_referral
from src.domain.user.vo import UserId


@dataclass
class GetReferralInfoInputDTO:
    user_id: int


@dataclass
class GetReferralInfoOutputDTO:
    referral_code: str
    referral_count: int


class GetReferralInfoInteractor(
    Interactor[GetReferralInfoInputDTO, GetReferralInfoOutputDTO | None]
):
    def __init__(
        self,
        user_repository: UserRepository,
        secret_key: str,
    ) -> None:
        self.user_repository = user_repository
        self.secret_key = secret_key

    async def __call__(
        self, data: GetReferralInfoInputDTO
    ) -> GetReferralInfoOutputDTO | None:
        user = await self.user_repository.get_user(UserId(data.user_id))

        if user is None:
            return None

        return GetReferralInfoOutputDTO(
            referral_code=encode_referral(data.user_id, self.secret_key),
            referral_count=int(user.referral_count),
        )
```

**Step 2: Update tests**

Replace `tests/unit/application/referral/test_get_info.py`:
```python
from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from src.application.referral.get_info import (
    GetReferralInfoInputDTO,
    GetReferralInfoInteractor,
    GetReferralInfoOutputDTO,
)
from src.domain.user import User
from src.domain.user.services.referral import decode_referral
from src.domain.user.vo import FirstName, ReferralCount, UserId


@pytest.fixture
def secret_key() -> str:
    return "test-secret"


@pytest.fixture
def user_repository() -> Mock:
    return Mock()


@pytest.fixture
def interactor(user_repository: Mock, secret_key: str) -> GetReferralInfoInteractor:
    return GetReferralInfoInteractor(
        user_repository=user_repository,
        secret_key=secret_key,
    )


@pytest.fixture
def sample_user() -> User:
    now = datetime.now(UTC)
    return User(
        id=UserId(123456789),
        first_name=FirstName("John"),
        last_name=None,
        username=None,
        bio=None,
        created_at=now,
        updated_at=now,
        last_login_at=now,
        referred_by=None,
        referral_count=ReferralCount(5),
    )


class TestGetReferralInfoInteractor:
    async def test_returns_referral_info(
        self,
        interactor: GetReferralInfoInteractor,
        user_repository: Mock,
        sample_user: User,
        secret_key: str,
    ) -> None:
        user_repository.get_user = AsyncMock(return_value=sample_user)

        result = await interactor(GetReferralInfoInputDTO(user_id=123456789))

        assert isinstance(result, GetReferralInfoOutputDTO)
        assert result.referral_count == 5
        # Verify code is decodable
        decoded = decode_referral(result.referral_code, secret_key)
        assert decoded == 123456789

    async def test_user_not_found_returns_none(
        self,
        interactor: GetReferralInfoInteractor,
        user_repository: Mock,
    ) -> None:
        user_repository.get_user = AsyncMock(return_value=None)

        result = await interactor(GetReferralInfoInputDTO(user_id=999))

        assert result is None
```

**Step 3: Run tests**

Run: `pytest tests/unit/application/referral/test_get_info.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add src/application/referral/get_info.py tests/unit/application/referral/test_get_info.py
git commit -m "refactor(referral): use encode_referral with secret key in get_info"
```

---

## Task 7: Создать локализацию

**Files:**
- Create: `locales/ru/stats.ftl`
- Create: `locales/en/stats.ftl`
- Create: `locales/ru/` directory if needed
- Create: `locales/en/` directory if needed

**Step 1: Create directories**

```bash
mkdir -p locales/ru locales/en
```

**Step 2: Create Russian locale**

Create `locales/ru/stats.ftl`:
```ftl
stats-overview =
    📊 Статистика

    Всего пользователей: { $total }
    По рефералам: { $referred } ({ $referred_pct }%)
    Органика: { $organic } ({ $organic_pct }%)

stats-top-inviters-btn = 🏆 Топ инвайтеров

stats-top-inviters-header = 🏆 Топ-{ $limit } инвайтеров:

stats-no-inviters = Пока нет инвайтеров
```

**Step 3: Create English locale**

Create `locales/en/stats.ftl`:
```ftl
stats-overview =
    📊 Statistics

    Total users: { $total }
    Referred: { $referred } ({ $referred_pct }%)
    Organic: { $organic } ({ $organic_pct }%)

stats-top-inviters-btn = 🏆 Top inviters

stats-top-inviters-header = 🏆 Top { $limit } inviters:

stats-no-inviters = No inviters yet
```

**Step 4: Commit**

```bash
git add locales/
git commit -m "feat(i18n): add statistics localization"
```

---

## Task 8: Создать админ-команду /stats

**Files:**
- Create: `src/presentation/bot/routers/admin/stats.py`
- Delete: `src/presentation/bot/routers/admin/example.py`
- Modify: `src/presentation/bot/routers/admin/__init__.py`

**Step 1: Create stats handler**

Create `src/presentation/bot/routers/admin/stats.py`:
```python
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
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
```

**Step 2: Update admin routers init**

Replace `src/presentation/bot/routers/admin/__init__.py`:
```python
from aiogram import Router

from src.presentation.bot.filters import AdminFilter

from . import stats


def setup_routers() -> Router:
    router = Router(name="admin routers")
    router.message.filter(AdminFilter())
    router.callback_query.filter(AdminFilter())
    router.include_routers(
        stats.router,
    )
    return router
```

**Step 3: Delete old example.py**

```bash
rm src/presentation/bot/routers/admin/example.py
```

**Step 4: Commit**

```bash
git add src/presentation/bot/routers/admin/
git commit -m "feat(admin): replace /example with /stats command

Add inline button for top inviters with i18n support."
```

---

## Task 9: Финальная проверка

**Step 1: Run all tests**

Run: `pytest -v`
Expected: All PASS

**Step 2: Run linter**

Run: `ruff check src tests`
Run: `ruff format src tests`

**Step 3: Fix any issues and commit**

```bash
git add -A
git commit -m "chore: fix linting issues"
```

**Step 4: Verify commits**

Run: `git log --oneline -15`

---

## Summary

После выполнения всех задач:

1. ✅ XOR-шифрование с секретным ключом вместо SHA256
2. ✅ ON DELETE RESTRICT + индекс в миграции
3. ✅ Интеракторы статистики (GetStatsInteractor, GetTopReferrersInteractor)
4. ✅ Методы репозитория для статистики
5. ✅ Админ-команда /stats с inline-кнопкой "Топ инвайтеров"
6. ✅ i18n для всех текстов (ru/en)
