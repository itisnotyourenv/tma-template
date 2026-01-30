from dishka import Provider, Scope, provide

from src.application.common.transaction import TransactionManager
from src.application.referral.get_info import GetReferralInfoInteractor
from src.application.referral.process import ProcessReferralInteractor
from src.application.referral.stats import GetStatsInteractor, GetTopReferrersInteractor
from src.domain.user import UserRepository
from src.infrastructure.config import Config


class ReferralInteractorProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def provide_process_referral_interactor(
        self,
        user_repository: UserRepository,
        transaction_manager: TransactionManager,
        config: Config,
    ) -> ProcessReferralInteractor:
        return ProcessReferralInteractor(
            user_repository=user_repository,
            transaction_manager=transaction_manager,
            secret_key=config.auth.secret_key,
        )

    @provide
    def provide_get_referral_info_interactor(
        self,
        user_repository: UserRepository,
        config: Config,
    ) -> GetReferralInfoInteractor:
        return GetReferralInfoInteractor(
            user_repository=user_repository,
            secret_key=config.auth.secret_key,
        )

    @provide
    def provide_get_stats_interactor(
        self,
        user_repository: UserRepository,
    ) -> GetStatsInteractor:
        return GetStatsInteractor(user_repository=user_repository)

    @provide
    def provide_get_top_referrers_interactor(
        self,
        user_repository: UserRepository,
    ) -> GetTopReferrersInteractor:
        return GetTopReferrersInteractor(user_repository=user_repository)
