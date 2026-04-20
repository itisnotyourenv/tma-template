from src.infrastructure.i18n import I18nProvider

from .auth import AuthProvider
from .db import DBProvider
from .interactors import interactor_providers

infra_providers = [
    AuthProvider(),
    I18nProvider(),
    DBProvider(),
]

__all__ = [
    "infra_providers",
    "interactor_providers",
]
