from src.domain.common.vo.base import BaseValueObject


class NonEmptyString(BaseValueObject[str]):
    __slots__ = ()

    min_length: int = 1
    max_length: int = 255

    @classmethod
    def _validate(cls, value: str) -> None:
        cls._validate_type(value)
        cls._validate_length(value)

    @classmethod
    def _validate_type(cls, value: str) -> None:
        if not isinstance(value, str):
            error_msg = (
                f"{cls.__name__} value must be a str, got {type(value).__name__!r}"
            )
            raise TypeError(error_msg)

    @classmethod
    def _validate_length(cls, value: str) -> None:
        if not (cls.min_length <= len(value) <= cls.max_length):
            error_msg = f"{cls.__name__} value must be between {cls.min_length} and {cls.max_length} characters long, got {len(value)}"
            raise ValueError(error_msg)
