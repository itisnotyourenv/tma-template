from src.domain.user.entity import User
from src.infrastructure.db.models.user import UserModel


class UserMapper:
    @staticmethod
    def to_domain(model: UserModel) -> User:
        return User(
            id=model.id,
            first_name=model.first_name,
            last_name=model.last_name,
            username=model.username,
            bio=model.bio,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login_at=model.last_login_at,
            referred_by=model.referred_by,
            referral_count=model.referral_count,
        )

    @staticmethod
    def to_model(user: User) -> UserModel:
        return UserModel(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            bio=user.bio,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at,
            referred_by=user.referred_by,
            referral_count=user.referral_count,
        )
