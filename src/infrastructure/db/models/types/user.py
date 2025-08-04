from typing import Optional, Any

from sqlalchemy import Integer, String, TypeDecorator, Dialect

from src.domain.user.vo import Bio, FirstName, LastName, UserId, Username


class UserIdType(TypeDecorator):
    impl = Integer
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, UserId):
            return value.value
        return value

    def process_result_value(self, value: Optional[Any], dialect: Dialect) -> UserId | None:
        if value is None:
            return None
        return UserId(value)


class FirstNameType(TypeDecorator):
    impl = String(64)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, FirstName):
            return value.value
        return value

    def process_result_value(self, value: Optional[Any], dialect: Dialect) -> FirstName | None:
        if value is None:
            return None
        return FirstName(value)


class LastNameType(TypeDecorator):
    impl = String(64)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, LastName):
            return value.value
        return value

    def process_result_value(self, value: Optional[Any], dialect: Dialect) -> LastName | None:
        if value is None:
            return None
        return LastName(value)


class UsernameType(TypeDecorator):
    impl = String(32)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, Username):
            return value.value
        return value

    def process_result_value(self, value: Optional[Any], dialect: Dialect) -> Username | None:
        if value is None:
            return None
        return Username(value)


class BioType(TypeDecorator):
    impl = String(160)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, Bio):
            return value.value
        return value

    def process_result_value(self, value: Optional[Any], dialect: Dialect) -> Bio | None:
        if value is None:
            return None
        return Bio(value)
