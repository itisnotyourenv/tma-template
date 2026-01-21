from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dishka.integrations.aiogram import inject

router = Router(name="admin")


@router.message(Command("example"))
@inject
async def example_admin_handler(message: Message) -> None:
    await message.answer(text="example admin command executed")
