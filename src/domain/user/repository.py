from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol, overload

from src.domain.user.entity import User
from src.domain.user.vo import UserId, Username


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


class UserRepository(Protocol):
    @overload
    async def get_user(self, identifier: UserId) -> User | None: ...

    @overload
    async def get_user(self, identifier: Username) -> User | None: ...

    @abstractmethod
    async def get_user(self, identifier: UserId | Username) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def create_user(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def update_user(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def delete_user(self, user_id: UserId) -> None: ...

    @abstractmethod
    async def set_referred_by(self, user_id: UserId, referrer_id: UserId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def increment_referral_count(self, user_id: UserId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_referral_stats(self) -> ReferralStats:
        """Get overall referral statistics."""
        ...

    @abstractmethod
    async def get_top_referrers(self, limit: int = 10) -> list[TopReferrer]:
        """Get top referrers by referral count."""
        ...
