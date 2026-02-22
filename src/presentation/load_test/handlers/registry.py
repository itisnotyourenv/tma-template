from typing import Protocol

from aiogram.types import Update


class UpdateFactory(Protocol):
    def __call__(self, update_id: int, user_id: int) -> Update: ...


_REGISTRY: dict[str, UpdateFactory] = {}


def register_handler(name: str):
    """Decorator to register an update factory by name."""

    def decorator(fn: UpdateFactory) -> UpdateFactory:
        if name in _REGISTRY:
            msg = f"Handler '{name}' already registered"
            raise ValueError(msg)
        _REGISTRY[name] = fn
        return fn

    return decorator


def get_handler(name: str) -> UpdateFactory:
    """Get a registered update factory by name."""
    if name not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY.keys()))
        msg = f"Unknown handler '{name}'. Available: {available}"
        raise ValueError(msg)
    return _REGISTRY[name]


def available_handlers() -> list[str]:
    """Return sorted list of registered handler names."""
    return sorted(_REGISTRY.keys())
