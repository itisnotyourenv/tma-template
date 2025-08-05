from .auth import AuthInteractorProvider
from .user import UserInteractorProvider

interactor_providers = [
    AuthInteractorProvider,
    UserInteractorProvider,
]

__all__ = [
    "AuthInteractorProvider",
    "AuthInteractorProvider",
    "interactor_providers",
]
