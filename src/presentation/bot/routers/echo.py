from aiogram import F, Router
from aiogram.types import Message
from fluentogram import TranslatorRunner

from src.presentation.bot.filters.admin import AdminFilter

router = Router(name="echo")

MEDIA_ATTRS = (
    "photo",
    "video",
    "document",
    "audio",
    "voice",
    "video_note",
    "sticker",
    "animation",
)


def _get_media_info(message: Message) -> str:
    """Extract detailed file info from a media message."""
    for attr in MEDIA_ATTRS:
        media = getattr(message, attr, None)
        if media is None:
            continue

        # photo is a list of PhotoSize, take the largest
        if attr == "photo":
            media = media[-1]

        lines = [
            f"<b>Type:</b> {attr}",
            f"<b>File ID:</b> <code>{media.file_id}</code>",
            f"<b>Unique ID:</b> <code>{media.file_unique_id}</code>",
        ]
        if hasattr(media, "file_size") and media.file_size is not None:
            lines.append(f"<b>Size:</b> {media.file_size} bytes")
        return "\n".join(lines)

    return ""


@router.message(
    AdminFilter(),
    F.photo
    | F.video
    | F.document
    | F.audio
    | F.voice
    | F.video_note
    | F.sticker
    | F.animation,
)
async def admin_media_handler(message: Message) -> None:
    """Return file_id info for media messages from admins."""
    info = _get_media_info(message)
    await message.answer(text=info)


@router.message()
async def echo_handler(message: Message, i18n: TranslatorRunner) -> None:
    """Catch-all for any unhandled messages."""
    await message.answer(text=i18n.get("echo-unknown-message"))
