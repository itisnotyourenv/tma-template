from sqlalchemy.orm import Mapped, mapped_column

from src.domain.user.entity import User
from src.domain.user.vo import Bio, FirstName, LastName, UserId, Username

from .base import BaseORMModel
from .types.user import BioType, FirstNameType, LastNameType, UserIdType, UsernameType


class UserModel(BaseORMModel):
    __tablename__ = "users"

    id: Mapped[UserId] = mapped_column(UserIdType, primary_key=True)
    first_name: Mapped[FirstName] = mapped_column(FirstNameType)
    last_name: Mapped[LastName | None] = mapped_column(LastNameType, nullable=True)
    username: Mapped[Username | None] = mapped_column(
        UsernameType, nullable=True, unique=False
    )
    bio: Mapped[Bio | None] = mapped_column(BioType, nullable=True)

    def to_domain(self) -> User:
        return User(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            username=self.username,
            bio=self.bio,
        )

    @classmethod
    def from_domain(cls, user: User) -> "UserModel":
        return cls(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            bio=user.bio,
        )
