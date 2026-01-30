"""
Limits from https://limits.tginfo.me/en
"""

from src.domain.common.vo.integer import PositiveInteger
from src.domain.common.vo.string import NonEmptyString


# Telegram related fields
class UserId(PositiveInteger):
    pass


class FirstName(NonEmptyString):
    min_length = 1
    max_length = 64


class LastName(NonEmptyString):
    min_length = 0
    max_length = 64


class Username(NonEmptyString):
    min_length = 4
    max_length = 32


# other fields
class Bio(NonEmptyString):
    min_length = 0
    max_length = 160


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

    def __hash__(self) -> int:
        return hash(self._value)

    def __repr__(self) -> str:
        return f"ReferralCount({self._value})"
