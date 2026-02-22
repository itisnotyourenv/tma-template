from aiogram.types import Message, Update

from src.presentation.load_test.factories import make_fake_chat, make_fake_user
from src.presentation.load_test.handlers.registry import register_handler


@register_handler("start")
def make_start_update(update_id: int, user_id: int) -> Update:
    """Create an Update with /start command."""
    user = make_fake_user(user_id)
    chat = make_fake_chat(user_id)

    message = Message(
        message_id=update_id,
        date=0,
        chat=chat,
        from_user=user,
        text="/start",
        entities=[{"type": "bot_command", "offset": 0, "length": 6}],
    )
    return Update(update_id=update_id, message=message)
