from aiogram.types import Chat, User


def make_fake_user(user_id: int) -> User:
    return User(
        id=user_id,
        is_bot=False,
        first_name=f"LoadTestUser_{user_id}",
        language_code="en",
    )


def make_fake_chat(chat_id: int) -> Chat:
    return Chat(id=chat_id, type="private")
