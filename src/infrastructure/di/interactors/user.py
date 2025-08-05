from dishka import Provider, Scope, provide

from src.application.user.get_me import GetUserProfileInteractor
from src.domain.user import UserRepository


class UserInteractorProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def provide_user_profile_interactor(
        self,
        user_repository: UserRepository,
    ) -> GetUserProfileInteractor:
        return GetUserProfileInteractor(
            user_repository,
        )
