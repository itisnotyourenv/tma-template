from .interactors import interactor_providers, AuthInteractorProvider
from .auth import AuthProvider
from .db import DBProvider

infra_providers = [
    AuthProvider,
    AuthInteractorProvider,
]

all_providers = interactor_providers.extend(infra_providers)

__all__ = [
    DBProvider,
    interactor_providers,
    infra_providers,
    all_providers,
]
