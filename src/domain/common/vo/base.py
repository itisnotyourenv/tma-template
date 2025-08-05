from abc import abstractmethod


class BaseValueObject[T]:
    __slots__ = ("_value",)

    def __init__(self, value: T) -> None:
        self.__class__._validate(value)
        self._value = value

    @classmethod
    @abstractmethod
    def _validate(cls, value: T) -> None: ...

    @property
    def value(self) -> T:
        return self._value

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return False
        return self.value == other.value  # type: ignore[attr-defined]

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._value!r})"
