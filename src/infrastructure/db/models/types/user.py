from sqlalchemy import BIGINT, INTEGER, Dialect, String, TypeDecorator

from src.domain.user.vo import Bio, FirstName, LastName, ReferralCount, UserId, Username


class UserIdType(TypeDecorator):
    impl = BIGINT
    cache_ok = True

    def process_bind_param(
        self, value: UserId | int | None, dialect: Dialect
    ) -> int | None:
        if value is None:
            return None
        if isinstance(value, UserId):
            return value.value
        return value

    def process_result_value(
        self, value: int | None, dialect: Dialect
    ) -> UserId | None:
        if value is None:
            return None
        return UserId(value)


class FirstNameType(TypeDecorator):
    impl = String(64)
    cache_ok = True

    def process_bind_param(
        self, value: FirstName | str | None, dialect: Dialect
    ) -> str | None:
        if value is None:
            return None
        if isinstance(value, FirstName):
            return value.value
        return value

    def process_result_value(
        self, value: str | None, dialect: Dialect
    ) -> FirstName | None:
        if value is None:
            return None
        return FirstName(value)


class LastNameType(TypeDecorator):
    impl = String(64)
    cache_ok = True

    def process_bind_param(
        self, value: LastName | str | None, dialect: Dialect
    ) -> str | None:
        if value is None:
            return None
        if isinstance(value, LastName):
            return value.value
        return value

    def process_result_value(
        self, value: str | None, dialect: Dialect
    ) -> LastName | None:
        if value is None:
            return None
        return LastName(value)


class UsernameType(TypeDecorator):
    impl = String(32)
    cache_ok = True

    def process_bind_param(
        self, value: Username | str | None, dialect: Dialect
    ) -> str | None:
        if value is None:
            return None
        if isinstance(value, Username):
            return value.value
        return value

    def process_result_value(
        self, value: str | None, dialect: Dialect
    ) -> Username | None:
        if value is None:
            return None
        return Username(value)


class BioType(TypeDecorator):
    impl = String(160)
    cache_ok = True

    def process_bind_param(
        self, value: Bio | str | None, dialect: Dialect
    ) -> str | None:
        if value is None:
            return None
        if isinstance(value, Bio):
            return value.value
        return value

    def process_result_value(self, value: str | None, dialect: Dialect) -> Bio | None:
        if value is None:
            return None
        return Bio(value)


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
