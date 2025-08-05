from .auth import AuthInteractorProvider

interactor_providers = [
    AuthInteractorProvider,
]

__all__ = [
    "AuthInteractorProvider",
    "interactor_providers",
]
