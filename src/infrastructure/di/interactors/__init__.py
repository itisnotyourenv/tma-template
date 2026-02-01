from .admin import AdminInteractorProvider
from .auth import AuthInteractorProvider
from .referral import ReferralInteractorProvider
from .user import UserInteractorProvider

interactor_providers = [
    AdminInteractorProvider,
    AuthInteractorProvider,
    ReferralInteractorProvider,
    UserInteractorProvider,
]

__all__ = [
    "AdminInteractorProvider",
    "AuthInteractorProvider",
    "ReferralInteractorProvider",
    "UserInteractorProvider",
    "interactor_providers",
]
