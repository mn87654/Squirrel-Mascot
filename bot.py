# bot.py
import asyncio, os
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from settings import settings
from database import (
    init_db, get_or_create_user, add_coins, set_coins, get_balance,
    can_claim_daily, claim_daily, list_active_tasks, add_task, remove_task,
    mark_task_complete, completed_today
)
from services import is_member, make_ref_link

# --- tiny HTTP server so Render health checks succeed ---
flask_app = Flask(__name__)

@flask_app.get("/")
def ok():
    return "Squirrel Coins Bot is running!"

def _run_http():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

def start_http():
    Thread(target=_run_http, daemon=True).start()

BOT = Bot(settings.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# --- helpers ---
def is_admin(user_id: int) -> bool:
    if not settings.ADMINS:
        return False
    return str(user_id) in {x.strip() for x in settings.ADMINS.split(",") if x.strip()}

def rainbow_title() -> str:
    return "🌈🧡💛💚💙💜 Squirrel Coins 💜💙💚💛🧡🌈"

# --- handlers ---
@dp.message(CommandStart())
async def start(message: Message):
    referrer = None
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1 and parts[1].startswith("ref_"):
        try:
            referrer = int(parts[1][4:])
        except Exception:
            referrer = None

    user, is_new = await get_or_create_user(message.from_user.id, referred_by=referrer)
    if is_new and referrer and referrer != message.from_user.id:
        await add_coins(referrer, settings.REFERRAL_REWARD)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Daily", callback_data="daily")],
        [InlineKeyboardButton(text="📝 Tasks", callback_data="tasks")],
        [InlineKeyboardButton(text="👥 Invite", callback_data="invite")],
        [InlineKeyboardButton(text="💰 Balance", callback_data="balance")],
    ])
    await message.answer(f"{rainbow_title()}\n\nWelcome to the Rainbow Squirrel world!", reply_markup=kb)

@dp.callback_query(F.data == "balance")
async def cb_balance(cb: CallbackQuery):
    bal = await get_balance(cb.from_user.id)
    await cb.message.edit_text(f"💰 Your Squirrel Coins: <b>{bal}</b>")
    await cb.answer()

@dp.message(Command("balance"))
async def cmd_balance(message: Message):
    bal = await get_balance(message.from_user.id)
    await message.reply(f"💰 Your Squirrel Coins: <b>{bal}</b>")
