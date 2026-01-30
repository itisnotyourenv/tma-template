from dataclasses import dataclass
from datetime import UTC, datetime

from src.domain.user import User, UserRepository
from src.domain.user.vo import FirstName, LastName, UserId, Username


@dataclass
class UpsertUserData:
    id: int
    username: str | None
    first_name: str
    last_name: str | None


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def upsert_user(self, data: UpsertUserData) -> User:
        user_id = UserId(data.id)

        existing_user = await self.user_repository.get_user(user_id)

        now = datetime.now(UTC)

        user = User(
            id=user_id,
            first_name=FirstName(data.first_name),
            last_name=LastName(data.last_name) if data.last_name else None,
            username=Username(data.username) if data.username else None,
            bio=existing_user.bio if existing_user else None,
            created_at=existing_user.created_at if existing_user else now,
            updated_at=now,
            last_login_at=now,
        )

        if existing_user is None:
            user = await self.user_repository.create_user(user)
        else:
            user = await self.user_repository.update_user(user)

        return user
