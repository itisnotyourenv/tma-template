# Referral System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement a referral tracking system where users can invite others via unique links and see how many people they invited.

**Architecture:** Add `referred_by` and `referral_count` fields to User model. Generate referral codes by hashing user ID. Process referrals in `/start` handler for new users only. Add `/referral` command to show link and stats.

**Tech Stack:** Python 3.13, aiogram 3.x, SQLAlchemy 2.x, Alembic, pytest

---

## Task 1: Add Referral Code Generation Service

**Files:**
- Create: `src/domain/user/services/__init__.py`
- Create: `src/domain/user/services/referral.py`
- Create: `tests/unit/domain/user/services/__init__.py`
- Create: `tests/unit/domain/user/services/test_referral.py`

**Step 1: Create test file with failing tests**

Create `tests/unit/domain/user/services/__init__.py`:
```python
```

Create `tests/unit/domain/user/services/test_referral.py`:
```python
import pytest

from src.domain.user.services.referral import generate_referral_code, find_referrer_id


class TestGenerateReferralCode:
    def test_returns_8_character_string(self):
        code = generate_referral_code(123456789)
        assert len(code) == 8
        assert isinstance(code, str)

    def test_deterministic_same_input_same_output(self):
        code1 = generate_referral_code(123456789)
        code2 = generate_referral_code(123456789)
        assert code1 == code2

    def test_different_inputs_different_outputs(self):
        code1 = generate_referral_code(123)
        code2 = generate_referral_code(456)
        assert code1 != code2

    def test_contains_only_hex_characters(self):
        code = generate_referral_code(999)
        assert all(c in "0123456789abcdef" for c in code)

    @pytest.mark.parametrize("user_id", [1, 100, 999999999, 9223372036854775807])
    def test_handles_various_user_ids(self, user_id):
        code = generate_referral_code(user_id)
        assert len(code) == 8


class TestFindReferrerId:
    def test_finds_existing_user(self):
        user_id = 123456789
        code = generate_referral_code(user_id)
        found = find_referrer_id(code, [111, 222, user_id, 333])
        assert found == user_id

    def test_returns_none_for_unknown_code(self):
        found = find_referrer_id("abcd1234", [111, 222, 333])
        assert found is None

    def test_returns_none_for_empty_list(self):
        found = find_referrer_id("abcd1234", [])
        assert found is None
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/domain/user/services/test_referral.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.domain.user.services'"

**Step 3: Write minimal implementation**

Create `src/domain/user/services/__init__.py`:
```python
```

Create `src/domain/user/services/referral.py`:
```python
import hashlib


def generate_referral_code(user_id: int) -> str:
    """Generate 8-character referral code from user ID using SHA256."""
    hash_input = f"referral:{user_id}".encode()
    hash_digest = hashlib.sha256(hash_input).hexdigest()
    return hash_digest[:8]


def find_referrer_id(code: str, user_ids: list[int]) -> int | None:
    """Find user ID by referral code. Returns None if not found."""
    for user_id in user_ids:
        if generate_referral_code(user_id) == code:
            return user_id
    return None
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/domain/user/services/test_referral.py -v`
Expected: PASS (all 8 tests)

**Step 5: Commit**

```bash
git add src/domain/user/services/ tests/unit/domain/user/services/
git commit -m "feat(referral): add referral code generation service

Add generate_referral_code() and find_referrer_id() functions
using SHA256 hash for deterministic code generation."
```

---

## Task 2: Add Referral Fields to User Model

**Files:**
- Modify: `src/domain/user/entity.py`
- Modify: `src/domain/user/vo.py`
- Modify: `src/infrastructure/db/models/user.py`
- Modify: `src/infrastructure/db/models/types/user.py`
- Modify: `tests/unit/domain/user/test_vo.py`

**Step 1: Add ReferralCount value object test**

Add to `tests/unit/domain/user/test_vo.py`:
```python
from src.domain.user.vo import ReferralCount


class TestReferralCount:
    @pytest.mark.parametrize("value,expected", [(0, 0), (1, 1), (100, 100)])
    def test_valid_referral_count(self, value, expected):
        rc = ReferralCount(value)
        assert rc.value == expected

    def test_negative_value_raises(self):
        with pytest.raises(ValueError):
            ReferralCount(-1)

    def test_invalid_type_raises(self):
        with pytest.raises((TypeError, ValueError)):
            ReferralCount("not a number")
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/domain/user/test_vo.py::TestReferralCount -v`
Expected: FAIL with "cannot import name 'ReferralCount'"

**Step 3: Add ReferralCount to vo.py**

Add to `src/domain/user/vo.py` at the end:
```python
class ReferralCount:
    """Non-negative integer for referral count."""

    def __init__(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("ReferralCount value must be an int")
        if value < 0:
            raise ValueError("ReferralCount cannot be negative")
        self._value = value

    @property
    def value(self) -> int:
        return self._value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ReferralCount):
            return self._value == other._value
        return False

    def __repr__(self) -> str:
        return f"ReferralCount({self._value})"
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/domain/user/test_vo.py::TestReferralCount -v`
Expected: PASS

**Step 5: Update User entity**

Modify `src/domain/user/entity.py`:
```python
from dataclasses import dataclass
from datetime import datetime

from .vo import Bio, FirstName, LastName, ReferralCount, UserId, Username


@dataclass
class User:
    id: UserId
    first_name: FirstName
    last_name: LastName | None
    username: Username | None
    bio: Bio | None
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime
    referred_by: UserId | None = None
    referral_count: ReferralCount | None = None
```

**Step 6: Add ReferralCountType to types/user.py**

Add to `src/infrastructure/db/models/types/user.py`:
```python
from sqlalchemy import INTEGER

from src.domain.user.vo import ReferralCount


class ReferralCountType(TypeDecorator):
    impl = INTEGER
    cache_ok = True

    def process_bind_param(
        self, value: ReferralCount | int | None, dialect: Dialect
    ) -> int | None:
        if value is None:
            return None
        if isinstance(value, ReferralCount):
            return value.value
        return value

    def process_result_value(
        self, value: int | None, dialect: Dialect
    ) -> ReferralCount | None:
        if value is None:
            return None
        return ReferralCount(value)
```

Also add import at top:
```python
from sqlalchemy import BIGINT, Dialect, String, TypeDecorator, INTEGER
```

And update `src/domain/user/vo` import:
```python
from src.domain.user.vo import Bio, FirstName, LastName, ReferralCount, UserId, Username
```

**Step 7: Update UserModel with referral fields**

Modify `src/infrastructure/db/models/user.py`:
```python
from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.user.entity import User
from src.domain.user.vo import Bio, FirstName, LastName, ReferralCount, UserId, Username

from .base import BaseORMModel
from .types.user import (
    BioType,
    FirstNameType,
    LastNameType,
    ReferralCountType,
    UserIdType,
    UsernameType,
)


class UserModel(BaseORMModel):
    __tablename__ = "users"

    id: Mapped[UserId] = mapped_column(UserIdType, primary_key=True)
    first_name: Mapped[FirstName] = mapped_column(FirstNameType)
    last_name: Mapped[LastName | None] = mapped_column(LastNameType, nullable=True)
    username: Mapped[Username | None] = mapped_column(
        UsernameType, nullable=True, unique=False
    )
    bio: Mapped[Bio | None] = mapped_column(BioType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_login_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    referred_by: Mapped[UserId | None] = mapped_column(
        UserIdType, ForeignKey("users.id"), nullable=True
    )
    referral_count: Mapped[ReferralCount] = mapped_column(
        ReferralCountType, nullable=False, server_default="0"
    )

    def to_domain(self) -> User:
        return User(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            username=self.username,
            bio=self.bio,
            created_at=self.created_at,
            updated_at=self.updated_at,
            last_login_at=self.last_login_at,
            referred_by=self.referred_by,
            referral_count=self.referral_count,
        )

    @classmethod
    def from_domain(cls, user: User) -> "UserModel":
        return cls(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            bio=user.bio,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at,
            referred_by=user.referred_by,
            referral_count=user.referral_count,
        )
```

**Step 8: Run all unit tests**

Run: `uv run pytest tests/unit/ -v`
Expected: PASS (update fixtures in test_create.py if needed to include new fields)

**Step 9: Commit**

```bash
git add src/domain/user/ src/infrastructure/db/models/
git commit -m "feat(user): add referred_by and referral_count fields

Add ReferralCount value object and update User entity and ORM model
with referral tracking fields."
```

---

## Task 3: Create Database Migration

**Files:**
- Create: `src/infrastructure/db/migrations/versions/YYYY_MM_DD_HHMM-xxxx_add_referral_fields.py`

**Step 1: Generate migration**

Run: `uv run alembic revision --autogenerate -m "add_referral_fields"`

**Step 2: Verify migration content**

The generated migration should contain:
```python
def upgrade() -> None:
    op.add_column('users', sa.Column('referred_by', sa.BIGINT(), nullable=True))
    op.add_column('users', sa.Column('referral_count', sa.INTEGER(), server_default='0', nullable=False))
    op.create_foreign_key(None, 'users', 'users', ['referred_by'], ['id'])


def downgrade() -> None:
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'referral_count')
    op.drop_column('users', 'referred_by')
```

**Step 3: Commit migration**

```bash
git add src/infrastructure/db/migrations/
git commit -m "feat(db): add migration for referral fields

Add referred_by (FK to users) and referral_count columns."
```

---

## Task 4: Add bot_username to Config

**Files:**
- Modify: `src/infrastructure/config.py`
- Modify: `tests/unit/infrastructure/test_config.py`

**Step 1: Add test for bot_username**

Add to `tests/unit/infrastructure/test_config.py` in appropriate test class:
```python
class TestTelegramConfig:
    def test_bot_username_required(self):
        with pytest.raises(ValidationError):
            TelegramConfig(
                bot_token="token",
                admin_ids=[1],
                # bot_username missing
            )

    def test_bot_username_valid(self):
        config = TelegramConfig(
            bot_token="token",
            admin_ids=[1],
            bot_username="my_bot",
        )
        assert config.bot_username == "my_bot"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/infrastructure/test_config.py::TestTelegramConfig -v`
Expected: FAIL

**Step 3: Add bot_username to TelegramConfig**

Modify `src/infrastructure/config.py` TelegramConfig class:
```python
class TelegramConfig(BaseModel):
    bot_token: str
    admin_ids: list[int]
    bot_username: str
    tg_init_data: str = "for-auth-endpoint-tests"
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/infrastructure/test_config.py::TestTelegramConfig -v`
Expected: PASS

**Step 5: Update config.yaml (example)**

Add `bot_username` to your config.yaml:
```yaml
telegram:
  bot_token: "..."
  admin_ids: [...]
  bot_username: "your_bot_username"
```

**Step 6: Commit**

```bash
git add src/infrastructure/config.py tests/unit/infrastructure/test_config.py
git commit -m "feat(config): add bot_username to TelegramConfig

Required for generating referral links."
```

---

## Task 5: Modify CreateUserInteractor to Return is_new Flag

**Files:**
- Modify: `src/application/user/create.py`
- Modify: `tests/unit/application/user/test_create.py`

**Step 1: Add test for is_new flag**

Add to `tests/unit/application/user/test_create.py`:
```python
async def test_create_new_user_returns_is_new_true(
    self,
    interactor,
    mock_user_repository,
    mock_transaction_manager,
    sample_create_user_input_dto,
    sample_user,
):
    mock_user_repository.get_user = AsyncMock(return_value=None)
    mock_user_repository.create_user = AsyncMock(return_value=sample_user)
    mock_transaction_manager.commit = AsyncMock()

    result = await interactor(sample_create_user_input_dto)

    assert result.is_new is True


async def test_update_existing_user_returns_is_new_false(
    self,
    interactor,
    mock_user_repository,
    mock_transaction_manager,
    sample_create_user_input_dto,
    sample_user,
):
    mock_user_repository.get_user = AsyncMock(return_value=sample_user)
    mock_user_repository.update_user = AsyncMock(return_value=sample_user)
    mock_transaction_manager.commit = AsyncMock()

    result = await interactor(sample_create_user_input_dto)

    assert result.is_new is False
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/application/user/test_create.py::TestCreateUserInteractor::test_create_new_user_returns_is_new_true -v`
Expected: FAIL with "AttributeError: 'CreateUserOutputDTO' object has no attribute 'is_new'"

**Step 3: Add is_new to CreateUserOutputDTO**

Modify `src/application/user/create.py`:
```python
@dataclass
class CreateUserOutputDTO:
    id: int
    username: str | None
    first_name: str
    last_name: str | None
    is_new: bool = False
```

And update the `__call__` method:
```python
async def __call__(self, data: CreateUserInputDTO) -> CreateUserOutputDTO:
    user_id = UserId(data.id)

    user = await self.user_repository.get_user(user_id)
    is_new = user is None

    if is_new:
        user = await self.user_repository.create_user(
            CreateUserDTO(
                id=data.id,
                username=data.username,
                first_name=data.first_name,
                last_name=data.last_name,
                is_premium=data.is_premium,
                photo_url=data.photo_url,
            ),
        )
    else:
        user = await self.user_repository.update_user(
            user_id=user_id,
            username=data.username,
            first_name=data.first_name,
            last_name=data.last_name,
            is_premium=data.is_premium,
            photo_url=data.photo_url,
        )

    await self.transaction_manager.commit()

    return CreateUserOutputDTO(
        id=user.id.value,
        username=user.username.value if user.username else None,
        first_name=user.first_name.value,
        last_name=user.last_name.value if user.last_name else None,
        is_new=is_new,
    )
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/application/user/test_create.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/application/user/create.py tests/unit/application/user/test_create.py
git commit -m "feat(user): add is_new flag to CreateUserOutputDTO

Allows distinguishing new users from returning users for referral processing."
```

---

## Task 6: Add ProcessReferralInteractor

**Files:**
- Create: `src/application/referral/__init__.py`
- Create: `src/application/referral/process.py`
- Create: `tests/unit/application/referral/__init__.py`
- Create: `tests/unit/application/referral/test_process.py`

**Step 1: Create test file**

Create `tests/unit/application/referral/__init__.py`:
```python
```

Create `tests/unit/application/referral/test_process.py`:
```python
from unittest.mock import AsyncMock, Mock

import pytest

from src.application.referral.process import (
    ProcessReferralInputDTO,
    ProcessReferralInteractor,
)
from src.domain.user.vo import UserId


class TestProcessReferralInteractor:
    @pytest.fixture
    def mock_user_repository(self):
        return Mock()

    @pytest.fixture
    def mock_transaction_manager(self):
        return Mock()

    @pytest.fixture
    def interactor(self, mock_user_repository, mock_transaction_manager):
        return ProcessReferralInteractor(
            user_repository=mock_user_repository,
            transaction_manager=mock_transaction_manager,
        )

    async def test_process_valid_referral(
        self, interactor, mock_user_repository, mock_transaction_manager
    ):
        # referrer_id=123 generates code via generate_referral_code
        from src.domain.user.services.referral import generate_referral_code

        referrer_id = 123
        new_user_id = 456
        code = generate_referral_code(referrer_id)

        mock_user_repository.get_all_user_ids = AsyncMock(
            return_value=[111, referrer_id, 222]
        )
        mock_user_repository.set_referred_by = AsyncMock()
        mock_user_repository.increment_referral_count = AsyncMock()
        mock_transaction_manager.commit = AsyncMock()

        input_dto = ProcessReferralInputDTO(
            new_user_id=new_user_id,
            referral_code=code,
        )

        result = await interactor(input_dto)

        assert result is True
        mock_user_repository.set_referred_by.assert_awaited_once_with(
            UserId(new_user_id), UserId(referrer_id)
        )
        mock_user_repository.increment_referral_count.assert_awaited_once_with(
            UserId(referrer_id)
        )
        mock_transaction_manager.commit.assert_awaited_once()

    async def test_referrer_not_found(
        self, interactor, mock_user_repository, mock_transaction_manager
    ):
        mock_user_repository.get_all_user_ids = AsyncMock(return_value=[111, 222])
        mock_transaction_manager.commit = AsyncMock()

        input_dto = ProcessReferralInputDTO(
            new_user_id=456,
            referral_code="unknown1",
        )

        result = await interactor(input_dto)

        assert result is False
        mock_user_repository.set_referred_by.assert_not_called()
        mock_user_repository.increment_referral_count.assert_not_called()

    async def test_self_referral_ignored(
        self, interactor, mock_user_repository, mock_transaction_manager
    ):
        from src.domain.user.services.referral import generate_referral_code

        user_id = 123
        code = generate_referral_code(user_id)

        mock_user_repository.get_all_user_ids = AsyncMock(return_value=[user_id])

        input_dto = ProcessReferralInputDTO(
            new_user_id=user_id,  # same as referrer
            referral_code=code,
        )

        result = await interactor(input_dto)

        assert result is False
        mock_user_repository.set_referred_by.assert_not_called()
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/application/referral/test_process.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Create implementation**

Create `src/application/referral/__init__.py`:
```python
```

Create `src/application/referral/process.py`:
```python
from dataclasses import dataclass

from src.application.common.interactor import Interactor
from src.application.common.transaction import TransactionManager
from src.domain.user import UserRepository
from src.domain.user.services.referral import find_referrer_id
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
    ) -> None:
        self.user_repository = user_repository
        self.transaction_manager = transaction_manager

    async def __call__(self, data: ProcessReferralInputDTO) -> bool:
        user_ids = await self.user_repository.get_all_user_ids()
        referrer_id = find_referrer_id(data.referral_code, user_ids)

        if referrer_id is None:
            return False

        if referrer_id == data.new_user_id:
            return False

        await self.user_repository.set_referred_by(
            UserId(data.new_user_id), UserId(referrer_id)
        )
        await self.user_repository.increment_referral_count(UserId(referrer_id))
        await self.transaction_manager.commit()

        return True
```

**Step 4: Add missing repository methods to protocol**

Add to `src/domain/user/repository.py`:
```python
@abstractmethod
async def get_all_user_ids(self) -> list[int]:
    raise NotImplementedError

@abstractmethod
async def set_referred_by(self, user_id: UserId, referrer_id: UserId) -> None:
    raise NotImplementedError

@abstractmethod
async def increment_referral_count(self, user_id: UserId) -> None:
    raise NotImplementedError
```

**Step 5: Add implementations to UserRepositoryImpl**

Add to `src/infrastructure/db/repos/user.py`:
```python
async def get_all_user_ids(self) -> list[int]:
    stmt = select(UserModel.id)
    result = await self._session.execute(stmt)
    return [row[0].value for row in result.fetchall()]

async def set_referred_by(self, user_id: UserId, referrer_id: UserId) -> None:
    stmt = (
        update(UserModel)
        .where(UserModel.id == user_id)
        .values(referred_by=referrer_id)
    )
    await self._session.execute(stmt)

async def increment_referral_count(self, user_id: UserId) -> None:
    stmt = (
        update(UserModel)
        .where(UserModel.id == user_id)
        .values(referral_count=UserModel.referral_count + 1)
    )
    await self._session.execute(stmt)
```

**Step 6: Run tests to verify they pass**

Run: `uv run pytest tests/unit/application/referral/test_process.py -v`
Expected: PASS

**Step 7: Commit**

```bash
git add src/application/referral/ src/domain/user/repository.py src/infrastructure/db/repos/user.py tests/unit/application/referral/
git commit -m "feat(referral): add ProcessReferralInteractor

Processes referral codes for new users, links them to referrer,
and increments referrer's count."
```

---

## Task 7: Add GetReferralInfoInteractor

**Files:**
- Create: `src/application/referral/get_info.py`
- Create: `tests/unit/application/referral/test_get_info.py`

**Step 1: Create test file**

Create `tests/unit/application/referral/test_get_info.py`:
```python
from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from src.application.referral.get_info import (
    GetReferralInfoInteractor,
    ReferralInfoOutputDTO,
)
from src.domain.user import User
from src.domain.user.vo import FirstName, ReferralCount, UserId


class TestGetReferralInfoInteractor:
    @pytest.fixture
    def mock_user_repository(self):
        return Mock()

    @pytest.fixture
    def interactor(self, mock_user_repository):
        return GetReferralInfoInteractor(user_repository=mock_user_repository)

    @pytest.fixture
    def sample_user(self):
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

    async def test_returns_referral_info(self, interactor, mock_user_repository, sample_user):
        mock_user_repository.get_user = AsyncMock(return_value=sample_user)

        result = await interactor(123456789)

        assert isinstance(result, ReferralInfoOutputDTO)
        assert result.referral_count == 5
        assert len(result.referral_code) == 8

    async def test_referral_code_is_deterministic(self, interactor, mock_user_repository, sample_user):
        mock_user_repository.get_user = AsyncMock(return_value=sample_user)

        result1 = await interactor(123456789)
        result2 = await interactor(123456789)

        assert result1.referral_code == result2.referral_code

    async def test_user_not_found_raises(self, interactor, mock_user_repository):
        mock_user_repository.get_user = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="User not found"):
            await interactor(999)
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/application/referral/test_get_info.py -v`
Expected: FAIL

**Step 3: Create implementation**

Create `src/application/referral/get_info.py`:
```python
from dataclasses import dataclass

from src.application.common.interactor import Interactor
from src.domain.user import UserRepository
from src.domain.user.services.referral import generate_referral_code
from src.domain.user.vo import UserId


@dataclass
class ReferralInfoOutputDTO:
    referral_code: str
    referral_count: int


class GetReferralInfoInteractor(Interactor[int, ReferralInfoOutputDTO]):
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def __call__(self, user_id: int) -> ReferralInfoOutputDTO:
        user = await self.user_repository.get_user(UserId(user_id))

        if user is None:
            raise ValueError("User not found")

        referral_code = generate_referral_code(user_id)
        referral_count = user.referral_count.value if user.referral_count else 0

        return ReferralInfoOutputDTO(
            referral_code=referral_code,
            referral_count=referral_count,
        )
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/application/referral/test_get_info.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/application/referral/get_info.py tests/unit/application/referral/test_get_info.py
git commit -m "feat(referral): add GetReferralInfoInteractor

Returns user's referral code and invitation count."
```

---

## Task 8: Register Referral Interactors in DI

**Files:**
- Create: `src/infrastructure/di/interactors/referral.py`
- Modify: `src/infrastructure/di/interactors/__init__.py`

**Step 1: Create ReferralInteractorProvider**

Create `src/infrastructure/di/interactors/referral.py`:
```python
from dishka import Provider, Scope, provide

from src.application.common.transaction import TransactionManager
from src.application.referral.get_info import GetReferralInfoInteractor
from src.application.referral.process import ProcessReferralInteractor
from src.domain.user import UserRepository


class ReferralInteractorProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def provide_process_referral_interactor(
        self,
        user_repository: UserRepository,
        transaction_manager: TransactionManager,
    ) -> ProcessReferralInteractor:
        return ProcessReferralInteractor(
            user_repository=user_repository,
            transaction_manager=transaction_manager,
        )

    @provide
    def provide_get_referral_info_interactor(
        self,
        user_repository: UserRepository,
    ) -> GetReferralInfoInteractor:
        return GetReferralInfoInteractor(
            user_repository=user_repository,
        )
```

**Step 2: Register in __init__.py**

Modify `src/infrastructure/di/interactors/__init__.py`:
```python
from .auth import AuthInteractorProvider
from .referral import ReferralInteractorProvider
from .user import UserInteractorProvider

interactor_providers = [
    AuthInteractorProvider,
    ReferralInteractorProvider,
    UserInteractorProvider,
]

__all__ = [
    "AuthInteractorProvider",
    "ReferralInteractorProvider",
    "interactor_providers",
]
```

**Step 3: Run unit tests to verify no regressions**

Run: `uv run pytest tests/unit/ -v`
Expected: PASS

**Step 4: Commit**

```bash
git add src/infrastructure/di/interactors/
git commit -m "feat(di): register referral interactors

Add ReferralInteractorProvider for ProcessReferral and GetReferralInfo."
```

---

## Task 9: Modify /start Handler for Referral Processing

**Files:**
- Modify: `src/presentation/bot/routers/commands.py`

**Step 1: Update /start handler**

Modify `src/presentation/bot/routers/commands.py`:
```python
from aiogram import Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from src.application.referral.process import (
    ProcessReferralInputDTO,
    ProcessReferralInteractor,
)
from src.application.user.create import CreateUserInputDTO, CreateUserInteractor

router = Router(name="commands")


@router.message(CommandStart())
@inject
async def command_start_handler(
    message: Message,
    command: CommandObject,
    interactor: FromDishka[CreateUserInteractor],
    process_referral: FromDishka[ProcessReferralInteractor],
) -> None:
    """This handler receives messages with `/start` command"""
    user = await interactor(
        data=CreateUserInputDTO(
            id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            is_premium=message.from_user.is_premium,
            photo_url=None,
        )
    )

    # Process referral for new users only
    if user.is_new and command.args and command.args.startswith("ref_"):
        referral_code = command.args[4:]  # Remove "ref_" prefix
        await process_referral(
            ProcessReferralInputDTO(
                new_user_id=message.from_user.id,
                referral_code=referral_code,
            )
        )

    msg = f"Hello, {user.first_name}!"
    await message.answer(text=msg)
```

**Step 2: Run unit tests**

Run: `uv run pytest tests/unit/ -v`
Expected: PASS

**Step 3: Commit**

```bash
git add src/presentation/bot/routers/commands.py
git commit -m "feat(bot): process referral codes in /start handler

Extract ref_ prefix from start parameter and process for new users."
```

---

## Task 10: Add /referral Command Handler

**Files:**
- Create: `src/presentation/bot/routers/referral.py`
- Modify: `src/presentation/bot/routers/__init__.py`

**Step 1: Create referral router**

Create `src/presentation/bot/routers/referral.py`:
```python
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from src.application.referral.get_info import GetReferralInfoInteractor
from src.infrastructure.config import Config

router = Router(name="referral")


@router.message(Command("referral"))
@inject
async def referral_handler(
    message: Message,
    get_referral_info: FromDishka[GetReferralInfoInteractor],
    config: FromDishka[Config],
) -> None:
    """Show user's referral link and statistics."""
    user_id = message.from_user.id
    info = await get_referral_info(user_id)

    bot_username = config.telegram.bot_username
    referral_link = f"https://t.me/{bot_username}?start=ref_{info.referral_code}"

    text = (
        f"Your referral link:\n"
        f"{referral_link}\n\n"
        f"Invited users: {info.referral_count}"
    )

    await message.answer(text=text)
```

**Step 2: Register router**

Modify `src/presentation/bot/routers/__init__.py`:
```python
from aiogram import Router

from .admin import setup_routers as setup_admin_routers
from .commands import router as commands_router
from .referral import router as referral_router


def setup_routers() -> Router:
    """Set up all bot routers."""
    main_router = Router()

    main_router.include_routers(
        # Command handlers first (highest priority)
        commands_router,
        referral_router,
        setup_admin_routers(),
    )

    return main_router


__all__ = ["setup_routers"]
```

**Step 3: Run unit tests**

Run: `uv run pytest tests/unit/ -v`
Expected: PASS

**Step 4: Commit**

```bash
git add src/presentation/bot/routers/
git commit -m "feat(bot): add /referral command handler

Shows user's referral link and invitation count."
```

---

## Task 11: Final Verification

**Step 1: Run all unit tests**

Run: `uv run pytest tests/unit/ -v`
Expected: All tests PASS

**Step 2: Run linting**

Run: `uv run ruff check src/ tests/`
Expected: No errors (fix any issues)

Run: `uv run ruff format src/ tests/`
Expected: Files formatted

**Step 3: Commit any fixes**

If there were linting fixes:
```bash
git add -A
git commit -m "style: fix linting issues"
```

**Step 4: Final commit summary**

Run: `git log --oneline -10`
Verify all commits are present.

---

## Summary

After completing all tasks, you will have:

1. **Domain layer:** `generate_referral_code()` and `find_referrer_id()` services
2. **User model:** `referred_by` and `referral_count` fields
3. **Database:** Migration for new columns
4. **Application layer:** `ProcessReferralInteractor` and `GetReferralInfoInteractor`
5. **Bot handlers:** Modified `/start` and new `/referral` command
6. **DI:** All interactors registered
7. **Config:** `bot_username` added

Total estimated tasks: 11
