from pydantic import BaseModel


class UserProfileResponse(BaseModel):
    """User profile response schema."""

    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    bio: str | None = None

    class Config:
        from_attributes = True
