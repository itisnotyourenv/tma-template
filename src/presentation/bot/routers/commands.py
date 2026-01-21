from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from src.application.user.create import CreateUserInputDTO, CreateUserInteractor

router = Router(name="commands")


@router.message(CommandStart())
@inject
async def command_start_handler(
    message: Message, interactor: FromDishka[CreateUserInteractor]
) -> None:
    """
    This handler receives messages with `/start` command
    """
    user = await interactor(
        data=CreateUserInputDTO(
            id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            is_premium=message.from_user.is_premium,
            photo_url=None,
        )
    )

    msg = f"Hello, {user.first_name}!"
    await message.answer(text=msg)
