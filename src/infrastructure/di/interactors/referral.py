from dishka import Provider, Scope, provide

from src.application.common.transaction import TransactionManager
from src.application.referral.get_info import GetReferralInfoInteractor
from src.application.referral.process import ProcessReferralInteractor
from src.domain.user import UserRepository


class ReferralInteractorProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def provide_process_referral_interactor(
        self,
        user_repository: UserRepository,
        transaction_manager: TransactionManager,
    ) -> ProcessReferralInteractor:
        return ProcessReferralInteractor(
            user_repository=user_repository,
            transaction_manager=transaction_manager,
        )

    @provide
    def provide_get_referral_info_interactor(
        self,
        user_repository: UserRepository,
    ) -> GetReferralInfoInteractor:
        return GetReferralInfoInteractor(
            user_repository=user_repository,
        )
