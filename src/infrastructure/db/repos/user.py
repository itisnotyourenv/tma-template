from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert

from src.domain.user.entity import User
from src.domain.user.repository import ReferralStats, TopReferrer, UserRepository
from src.domain.user.vo import UserId, Username
from src.infrastructure.db.mappers import UserMapper
from src.infrastructure.db.models.user import UserModel
from src.infrastructure.db.repos.base import BaseSQLAlchemyRepo


class UserRepositoryImpl(UserRepository, BaseSQLAlchemyRepo):
    async def get_user(self, identifier: UserId | Username) -> User | None:
        if isinstance(identifier, UserId):
            stmt = select(UserModel).where(UserModel.id == identifier)
        else:  # by == "username"
            stmt = select(UserModel).where(UserModel.username == identifier)

        result = await self._session.execute(stmt)

        user_model = result.scalars().first()

        return UserMapper.to_domain(user_model) if user_model else None

    async def create_user(self, user: User) -> User:
        stmt = (
            insert(UserModel)
            .values(
                id=user.id.value,
                username=user.username.value if user.username else None,
                first_name=user.first_name.value,
                last_name=user.last_name.value if user.last_name else None,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login_at=user.last_login_at,
            )
            .returning(UserModel)
        )

        result = await self._session.execute(stmt)
        orm_model = result.scalar_one()
        return UserMapper.to_domain(orm_model)

    async def update_user(self, user: User) -> User:
        stmt = (
            update(UserModel)
            .where(UserModel.id == user.id.value)
            .values(
                username=user.username.value if user.username else None,
                first_name=user.first_name.value,
                last_name=user.last_name.value if user.last_name else None,
                updated_at=user.updated_at,
                last_login_at=user.last_login_at,
            )
            .returning(UserModel)
        )
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one()
        return UserMapper.to_domain(orm_model)

    async def delete_user(self, user_id: UserId) -> None:
        raise NotImplementedError

    async def set_referred_by(self, user_id: UserId, referrer_id: UserId) -> None:
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(referred_by=referrer_id)
        )
        await self._session.execute(stmt)

    async def increment_referral_count(self, user_id: UserId) -> None:
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(referral_count=UserModel.referral_count + 1)
        )
        await self._session.execute(stmt)

    async def get_referral_stats(self) -> ReferralStats:
        total_query = select(func.count()).select_from(UserModel)
        referred_query = (
            select(func.count())
            .select_from(UserModel)
            .where(UserModel.referred_by.isnot(None))
        )

        total = (await self._session.execute(total_query)).scalar() or 0
        referred = (await self._session.execute(referred_query)).scalar() or 0

        return ReferralStats(
            total_users=total,
            referred_count=referred,
            organic_count=total - referred,
        )

    async def get_top_referrers(self, limit: int = 10) -> list[TopReferrer]:
        query = (
            select(UserModel)
            .where(UserModel.referral_count > 0)
            .order_by(UserModel.referral_count.desc())
            .limit(limit)
        )
        result = await self._session.execute(query)
        users = result.scalars().all()

        return [
            TopReferrer(
                user_id=u.id.value,
                username=u.username.value if u.username else None,
                first_name=u.first_name.value,
                referral_count=u.referral_count.value,
            )
            for u in users
        ]
