# User Timestamp Fields Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add `created_at`, `updated_at`, and `last_login_at` UTC-aware datetime fields to the User entity and model.

**Architecture:** Domain layer gets three datetime fields. Persistence layer uses SQLAlchemy's `server_default` and `onupdate` for auto-management. Repository explicitly updates `last_login_at` on user interactions.

**Tech Stack:** Python 3.13, SQLAlchemy, Alembic, PostgreSQL, pytest

---

## Task 1: Update Domain Entity

**Files:**
- Modify: `src/domain/user/entity.py`

**Step 1: Add datetime import and fields**

Edit `src/domain/user/entity.py` to add the three timestamp fields:

```python
from dataclasses import dataclass
from datetime import datetime

from .vo import Bio, FirstName, LastName, UserId, Username


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
```

**Step 2: Commit**

```bash
git add src/domain/user/entity.py
git commit -m "feat(domain): add timestamp fields to User entity"
```

---

## Task 2: Update ORM Model

**Files:**
- Modify: `src/infrastructure/db/models/user.py`

**Step 1: Add timestamp columns to UserModel**

Edit `src/infrastructure/db/models/user.py`:

```python
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.user.entity import User
from src.domain.user.vo import Bio, FirstName, LastName, UserId, Username

from .base import BaseORMModel
from .types.user import BioType, FirstNameType, LastNameType, UserIdType, UsernameType


class UserModel(BaseORMModel):
    __tablename__ = "users"

    id: Mapped[UserId] = mapped_column(UserIdType, primary_key=True)
    first_name: Mapped[FirstName] = mapped_column(FirstNameType)
    last_name: Mapped[LastName | None] = mapped_column(LastNameType, nullable=True)
    username: Mapped[Username | None] = mapped_column(
        UsernameType, nullable=True, unique=False
    )
    bio: Mapped[Bio | None] = mapped_column(BioType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
    last_login_at: Mapped[datetime] = mapped_column(server_default=func.now())

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
        )
```

**Step 2: Commit**

```bash
git add src/infrastructure/db/models/user.py
git commit -m "feat(db): add timestamp columns to UserModel"
```

---

## Task 3: Create Alembic Migration

**Files:**
- Create: `src/infrastructure/db/migrations/versions/2026_01_24_user_timestamps.py`

**Step 1: Generate migration**

Run:
```bash
cd /Users/zurabubaev/PycharmProjects/tma_template && alembic revision -m "add_user_timestamps"
```

**Step 2: Edit migration file**

Edit the generated migration file to add the three columns:

```python
"""add_user_timestamps

Revision ID: <generated>
Revises: c6ae99a6b811
Create Date: 2026-01-24 ...

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "<generated>"
down_revision: str | Sequence[str] | None = "c6ae99a6b811"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "last_login_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "last_login_at")
    op.drop_column("users", "updated_at")
    op.drop_column("users", "created_at")
```

**Step 3: Commit**

```bash
git add src/infrastructure/db/migrations/versions/
git commit -m "feat(db): add migration for user timestamp columns"
```

---

## Task 4: Update Repository to Set last_login_at

**Files:**
- Modify: `src/infrastructure/db/repos/user.py`

**Step 1: Update update_user method**

Edit `src/infrastructure/db/repos/user.py` to set `last_login_at` when updating:

```python
from datetime import datetime, timezone
from typing import Unpack

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from src.domain.user.entity import User
from src.domain.user.repository import CreateUserDTO, UpdateUserDTO, UserRepository
from src.domain.user.vo import UserId, Username
from src.infrastructure.db.models.user import UserModel
from src.infrastructure.db.repos.base import BaseSQLAlchemyRepo


class UserRepositoryImpl(UserRepository, BaseSQLAlchemyRepo):
    async def get_user(self, identifier: UserId | Username) -> User | None:
        if isinstance(identifier, UserId):
            stmt = select(UserModel).where(UserModel.id == identifier)
        else:  # by == "username"
            stmt = select(UserModel).where(UserModel.username == identifier)

        result = await self._session.execute(stmt)

        user_model = result.scalars().first()

        return user_model.to_domain() if user_model else None

    async def create_user(self, user: CreateUserDTO) -> User:
        stmt = (
            insert(UserModel)
            .values(
                id=user["id"],
                username=user["username"],
                first_name=user["first_name"],
                last_name=user["last_name"],
            )
            .returning(UserModel)
        )

        result = await self._session.execute(stmt)
        orm_model = result.scalar_one()
        return orm_model.to_domain()

    async def update_user(
        self, user_id: UserId, **fields: Unpack[UpdateUserDTO]
    ) -> User:
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(
                username=fields["username"],
                first_name=fields["first_name"],
                last_name=fields["last_name"],
                last_login_at=datetime.now(timezone.utc),
            )
            .returning(UserModel)
        )
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one()
        return orm_model.to_domain()

    async def delete_user(self, user_id: UserId) -> None:
        raise NotImplementedError
```

**Step 2: Commit**

```bash
git add src/infrastructure/db/repos/user.py
git commit -m "feat(repo): update last_login_at on user updates"
```

---

## Task 5: Update Test Factory

**Files:**
- Modify: `tests/utils/model_factories/user.py`

**Step 1: Add timestamp fields to factory**

Edit `tests/utils/model_factories/user.py`:

```python
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone

import factory
import pytest

from src.infrastructure.db.models import UserModel

from .base import BaseFactory, create_entity


class UserModelFactory(BaseFactory):
    class Meta:
        model = UserModel

    id = factory.Sequence(lambda n: n + 1)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.Faker("name")
    bio = factory.Faker("sentence")
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    last_login_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


@pytest.fixture(scope="function")
def patch_user_session(native_db_session):
    UserModelFactory._meta.sqlalchemy_session = native_db_session  # type: ignore


@pytest.fixture(scope="function")
async def create_user(patch_user_session) -> Callable[..., Awaitable[UserModel]]:
    async def _create(**kwargs):
        return await create_entity(UserModelFactory, **kwargs)

    return _create


@pytest.fixture(scope="function")
async def test_user(
    create_user: Callable[..., Awaitable[UserModel]],
) -> UserModel:
    return await create_user()
```

**Step 2: Commit**

```bash
git add tests/utils/model_factories/user.py
git commit -m "feat(tests): add timestamp fields to UserModelFactory"
```

---

## Task 6: Run Tests and Verify

**Step 1: Run existing tests**

Run:
```bash
pytest tests/ -v
```

Expected: All tests pass

**Step 2: Final commit if any fixes needed**

If tests reveal issues, fix and commit.

---

## Summary

| Task | Description |
|------|-------------|
| 1 | Update domain entity with 3 datetime fields |
| 2 | Update ORM model with columns and mapping |
| 3 | Create Alembic migration |
| 4 | Update repository to set last_login_at |
| 5 | Update test factory |
| 6 | Run tests and verify |