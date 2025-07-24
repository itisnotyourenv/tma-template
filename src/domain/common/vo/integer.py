from src.domain.common.vo.base import BaseValueObject


class PositiveInteger(BaseValueObject[int]):
    __slots__ = ()

    @classmethod
    def _validate(cls, value: int) -> None:
        cls._validate_type(value)
        cls._validate_positive(value)

    @classmethod
    def _validate_type(cls, value: int) -> None:
        if not isinstance(value, int):
            error_msg = (
                f"{cls.__name__} value must be an int, got {type(value).__name__!r}"
            )
            raise TypeError(error_msg)

    @classmethod
    def _validate_positive(cls, value: int) -> None:
        if value <= 0:
            error_msg = f"{cls.__name__} value must be a positive integer, got {value}"
            raise ValueError(error_msg)
