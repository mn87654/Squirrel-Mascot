# bot.py — Webhook version for Render (Aiogram 3.x)
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from settings import settings
from database import (
    init_db, get_or_create_user,
    add_coins, set_balance, get_balance
)

# Initialize bot & dispatcher
BOT = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()


# --- Commands ---
@dp.message(CommandStart())
async def cmd_start(message: Message):
    print(f"✅ /start received from {message.from_user.id}")
    await message.answer(
        "🌈💜💛🧡 Squirrel Coins 💜💛🧡🌈\n\n"
        "Welcome to the Rainbow Squirrel world!"
    )

@dp.message(Command("balance"))
async def cmd_balance(message: Message):
    user = await get_or_create_user(message.from_user.id)
    print(f"✅ /balance requested by {message.from_user.id}, balance={user.balance}")
    await message.answer(f"💰 Your balance: {user.balance} coins")

@dp.message(Command("ping"))
async def cmd_ping(message: Message):
    print(f"✅ /ping received from {message.from_user.id}")
    await message.answer("pong")


# --- Universal handler (for testing) ---
@dp.message()
async def all_messages(message: Message):
    print(f"📩 Got message: {message.text} from {message.from_user.id}")
    await message.reply("I got your message ✅")


# --- Webhook setup ---
async def on_startup(app: web.Application):
    print("🚀 Bot is starting, initializing DB...")
    await init_db()
    await BOT.set_webhook(f"https://{settings.RENDER_EXTERNAL_HOSTNAME}/webhook")

async def on_shutdown(app: web.Application):
    print("🛑 Bot shutting down...")
    await BOT.delete_webhook()


def main():
    app = web.Application()
    SimpleRequestHandler(dp, BOT).register(app, path="/webhook")
    setup_application(app, dp, on_startup=on_startup, on_shutdown=on_shutdown)
    web.run_app(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))


if __name__ == "__main__":
    main()
