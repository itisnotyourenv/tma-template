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

    @property
    def is_new(self) -> bool:
        return self.created_at == self.last_login_at
