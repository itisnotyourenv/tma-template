from dataclasses import dataclass
from datetime import datetime

from .vo import Bio, FirstName, LanguageCode, LastName, ReferralCount, UserId, Username


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
    language_code: LanguageCode | None = None

    @property
    def is_new(self) -> bool:
        return self.created_at == self.last_login_at

    def __str__(self) -> str:
        return (
            f"User(id={self.id}, username={self.username}, "
            f"first_name={self.first_name}, last_name={self.last_name}, "
            f"language_code={self.language_code}, is_new={self.is_new})"
        )
