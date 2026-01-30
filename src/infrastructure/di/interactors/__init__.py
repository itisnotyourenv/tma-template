from .auth import AuthInteractorProvider
from .referral import ReferralInteractorProvider
from .user import UserInteractorProvider

interactor_providers = [
    AuthInteractorProvider,
    ReferralInteractorProvider,
    UserInteractorProvider,
]

__all__ = [
    "AuthInteractorProvider",
    "ReferralInteractorProvider",
    "UserInteractorProvider",
    "interactor_providers",
]
