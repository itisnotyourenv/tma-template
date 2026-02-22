import importlib
from pathlib import Path

from .registry import available_handlers, get_handler, register_handler

# Auto-import all handler modules to trigger @register_handler
for _f in Path(__file__).parent.glob("*.py"):
    if _f.name not in ("__init__.py", "registry.py"):
        importlib.import_module(f".{_f.stem}", __package__)

__all__ = ["available_handlers", "get_handler", "register_handler"]
