from dishka import Provider, Scope, provide

from src.application.auth.tg import AuthTgInteractor
from src.application.common.transaction import TransactionManager
from src.application.interfaces.auth import AuthService
from src.application.user.service import UserService


class AuthInteractorProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def provide_auth_tg_interactor(
        self,
        user_service: UserService,
        transaction_manager: TransactionManager,
        auth_service: AuthService,
    ) -> AuthTgInteractor:
        return AuthTgInteractor(
            user_service,
            transaction_manager,
            auth_service,
        )
