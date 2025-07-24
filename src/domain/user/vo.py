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
