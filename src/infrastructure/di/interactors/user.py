from dishka import Provider, Scope, provide

from src.application.common.transaction import TransactionManager
from src.application.user.create import CreateUserInteractor
from src.application.user.get_me import GetUserProfileInteractor
from src.application.user.interactors.update_language import UpdateLanguageInteractor
from src.application.user.service import UserService
from src.domain.user import UserRepository


class UserInteractorProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def provide_user_service(
        self,
        user_repository: UserRepository,
    ) -> UserService:
        return UserService(user_repository)

    @provide
    def provide_user_profile_interactor(
        self,
        user_repository: UserRepository,
    ) -> GetUserProfileInteractor:
        return GetUserProfileInteractor(
            user_repository,
        )

    @provide
    def provide_create_user_interactor(
        self,
        user_service: UserService,
        transaction_manager: TransactionManager,
    ) -> CreateUserInteractor:
        return CreateUserInteractor(
            user_service=user_service,
            transaction_manager=transaction_manager,
        )

    @provide
    def provide_update_language_interactor(
        self,
        user_repository: UserRepository,
        transaction_manager: TransactionManager,
    ) -> UpdateLanguageInteractor:
        return UpdateLanguageInteractor(
            user_repository=user_repository,
            transaction_manager=transaction_manager,
        )
