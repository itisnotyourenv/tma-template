from dishka import Provider, Scope, provide

from src.application.admin import CheckAliveInteractor
from src.domain.admin import AdminRepository


class AdminInteractorProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def provide_check_alive_interactor(
        self,
        admin_repository: AdminRepository,
    ) -> CheckAliveInteractor:
        return CheckAliveInteractor(admin_repository=admin_repository)
