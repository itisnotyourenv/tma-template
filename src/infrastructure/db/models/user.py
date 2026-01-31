from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.user.vo import Bio, FirstName, LastName, ReferralCount, UserId, Username

from .base import BaseORMModel
from .types.user import (
    BioType,
    FirstNameType,
    LastNameType,
    ReferralCountType,
    UserIdType,
    UsernameType,
)


class UserModel(BaseORMModel):
    __tablename__ = "users"

    id: Mapped[UserId] = mapped_column(UserIdType, primary_key=True)
    first_name: Mapped[FirstName] = mapped_column(FirstNameType)
    last_name: Mapped[LastName | None] = mapped_column(LastNameType, nullable=True)
    username: Mapped[Username | None] = mapped_column(
        UsernameType, nullable=True, unique=False
    )
    bio: Mapped[Bio | None] = mapped_column(BioType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_login_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    referred_by: Mapped[UserId | None] = mapped_column(
        UserIdType, ForeignKey("users.id"), nullable=True
    )
    referral_count: Mapped[ReferralCount] = mapped_column(
        ReferralCountType, nullable=False, server_default="0"
    )
