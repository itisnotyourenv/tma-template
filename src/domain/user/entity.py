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
