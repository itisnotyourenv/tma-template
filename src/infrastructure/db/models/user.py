from typing import Optional

from sqlalchemy import Column
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.user.entity import User
from src.domain.user.vo import UserId, FirstName, LastName, Username, Bio

from .base import BaseORMModel
from .types.user import UserIdType, FirstNameType, LastNameType, UsernameType, BioType


class UserModel(BaseORMModel):
    __tablename__ = "users"

    id: Mapped[UserId] = mapped_column(UserIdType, primary_key=True)
    first_name: Mapped[FirstName] = mapped_column(FirstNameType)
    last_name: Mapped[Optional[LastName]] = mapped_column(LastNameType, nullable=True)
    username: Mapped[Optional[Username]] = mapped_column(
        UsernameType, nullable=True, unique=False
    )
    bio: Mapped[Optional[Bio]] = Column(BioType, nullable=True)

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
