from dataclasses import dataclass

from src.domain.user.vo import UserId

from .vo import QuestionText


@dataclass
class Question:
    id: str
    text: QuestionText
    sender_id: UserId
    receiver_id: UserId
    is_read: bool
    is_public: bool
