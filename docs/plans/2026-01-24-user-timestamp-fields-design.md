# User Timestamp Fields Design

## Overview

Add `created_at`, `updated_at`, and `last_login_at` timestamp fields to the User entity and model.

## Requirements

- **`created_at`**: Set automatically when user is created
- **`updated_at`**: Set automatically on creation, updates on any row change
- **`last_login_at`**: Set to `created_at` on creation, updates on every user interaction
- All timestamps are UTC-aware datetimes
- Timestamps are part of the domain layer (User entity)
- Timestamps are NOT exposed via the API (internal only)

## Implementation

### Domain Layer

**File**: `src/domain/user/entity.py`

Add three required datetime fields to the User dataclass:

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

### Persistence Layer

**File**: `src/infrastructure/db/models/user.py`

Add three columns with SQLAlchemy auto-management:

```python
from datetime import datetime, timezone
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

created_at: Mapped[datetime] = mapped_column(server_default=func.now())
updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
last_login_at: Mapped[datetime] = mapped_column(server_default=func.now())
```

Update `to_domain()` and `from_domain()` methods to include these fields.

### Migration

Create new Alembic migration adding three columns to the `users` table with `server_default=func.now()` so existing rows get populated.

### Repository

**File**: `src/infrastructure/db/repos/user.py`

When updating user data, explicitly set `last_login_at`:

```python
from datetime import datetime, timezone

user_model.last_login_at = datetime.now(timezone.utc)
```

### Test Factory

**File**: `tests/utils/model_factories/user.py`

Add datetime defaults for the three new fields:

```python
from datetime import datetime, timezone

created_at = datetime.now(timezone.utc)
updated_at = datetime.now(timezone.utc)
last_login_at = datetime.now(timezone.utc)
```

## Files Changed

| File | Change |
|------|--------|
| `src/domain/user/entity.py` | Add 3 datetime fields |
| `src/infrastructure/db/models/user.py` | Add 3 columns, update mapping methods |
| `src/infrastructure/db/repos/user.py` | Set `last_login_at` on updates |
| `src/infrastructure/db/migrations/versions/...` | New migration |
| `tests/utils/model_factories/user.py` | Add datetime defaults |

## Not Changed

- API schemas (`src/presentation/api/user/schemas.py`) — timestamps are internal only
