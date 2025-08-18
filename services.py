# services.py
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ChatMemberAdministrator, ChatMemberOwner, ChatMemberMember

async def is_member(bot: Bot, channel: str | int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        return isinstance(member, (ChatMemberMember, ChatMemberAdministrator, ChatMemberOwner))
    except TelegramBadRequest:
        return False

def make_ref_link(bot_username: str, user_id: int) -> str:
    return f"https://t.me/{bot_username}?start=ref_{user_id}"
