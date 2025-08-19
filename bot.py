# bot.py — Webhook version for Render (Aiogram 3.x)
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.client.default import DefaultBotProperties

from settings import settings
from database import (
    init_db, get_or_create_user, add_coins, set_coins, get_balance,
    can_claim_daily, claim_daily, list_active_tasks, add_task, remove_task,
    mark_task_complete, completed_today
)
from services import is_member, make_ref_link


# ---------------- Bot Setup ----------------
BOT = Bot(
    settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher()

# ---------------- Webhook URL Setup ----------------
RENDER_URL = os.getenv("RENDER_URL") or f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}"
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{RENDER_URL}{WEBHOOK_PATH}"


# ---------------- Helpers ----------------
def is_admin(user_id: int) -> bool:
    if not settings.ADMINS:
        return False
    return str(user_id) in {x.strip() for x in settings.ADMINS.split(",") if x.strip()}

def rainbow_title() -> str:
    return "🌈💜💛🧡 Squirrel Coins 💜💛🧡🌈"


# ---------------- Handlers ----------------
@dp.message(CommandStart())
async def start_cmd(message: Message):
    print(f"✅ /start received from {message.from_user.id}")   # Debug log

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
        [InlineKeyboardButton(text="📅 Daily", callback_data="daily")],
        [InlineKeyboardButton(text="📝 Tasks", callback_data="tasks")],
        [InlineKeyboardButton(text="🤝 Invite", callback_data="invite")],
        [InlineKeyboardButton(text="💰 Balance", callback_data="balance")],
    ])

    await message.answer(
        f"{rainbow_title()}\n\nWelcome to the Rainbow Squirrel world!",
        reply_markup=kb
    )


@dp.callback_query(F.data == "balance")
async def cb_balance(cb: CallbackQuery):
    print(f"💰 Balance callback from {cb.from_user.id}")   # Debug log
    bal = await get_balance(cb.from_user.id)
    await cb.message.edit_text(f"💰 Your Squirrel Coins: <b>{bal}</b>")
    await cb.answer()


@dp.message(Command("balance"))
async def cmd_balance(message: Message):
    print(f"💰 /balance command from {message.from_user.id}")   # Debug log
    bal = await get_balance(message.from_user.id)
    await message.reply(f"💰 Your Squirrel Coins: <b>{bal}</b>")


# ✅ Extra Test Command
@dp.message(Command("ping"))
async def cmd_ping(message: Message):
    print(f"🏓 Ping received from {message.from_user.id}")   # Debug log
    await message.reply("🏓 Pong!")


# ---------------- Webhook lifecycle ----------------
async def on_startup(app):
    print("🚀 Starting up... setting webhook")
    await BOT.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    print(f"✅ Webhook set: {WEBHOOK_URL}")

async def on_shutdown(app):
    print("🛑 Shutting down... deleting webhook")
    await BOT.delete_webhook()
    print("🛑 Webhook deleted")


def build_app():
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # ✅ Health check route
    async def health(request):
        print("👀 Health check called")
        return web.Response(text="OK")
    app.router.add_get("/", health)

    # Register Telegram webhook handler
    SimpleRequestHandler(dp, BOT).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=BOT)
    return app


if __name__ == "__main__":
    web.run_app(build_app(), host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
