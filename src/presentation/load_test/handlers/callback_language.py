from aiogram.types import CallbackQuery, Message, Update

from src.presentation.load_test.factories import make_fake_chat, make_fake_user
from src.presentation.load_test.handlers.registry import register_handler


@register_handler("callback_language")
def make_callback_language_update(update_id: int, user_id: int) -> Update:
    """Create an Update with CallbackQuery for language selection."""
    user = make_fake_user(user_id)
    chat = make_fake_chat(user_id)

    message = Message(
        message_id=update_id - 1,
        date=0,
        chat=chat,
        from_user=user,
        text="Choose language:",
    )
    callback = CallbackQuery(
        id=str(update_id),
        chat_instance=str(user_id),
        from_user=user,
        message=message,
        data="onboarding:en",
    )
    return Update(update_id=update_id, callback_query=callback)
