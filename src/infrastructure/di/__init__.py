from src.infrastructure.i18n import I18nProvider

from .auth import AuthProvider
from .db import DBProvider
from .interactors import AuthInteractorProvider, interactor_providers

infra_providers = [
    AuthProvider,
    AuthInteractorProvider,
]

__all__ = [
    "DBProvider",
    "I18nProvider",
    "infra_providers",
    "interactor_providers",
]
