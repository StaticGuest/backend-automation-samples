import asyncio
import logging
import os
import sys
from telebot.async_telebot import AsyncTeleBot
from dotenv import load_dotenv

from main import fetch_symbol_price, CONFIG as MARKET_CONFIG

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("TelegramDaemon")

bot = AsyncTeleBot(TOKEN)

def is_authorized(user_id: int, username: str = "") -> bool:
    allowed = user_id in ADMIN_IDS
    if not allowed:
        logger.warning(f"Unauthorized access attempt by ID {user_id} (@{username})")
    return allowed

@bot.message_handler(commands=['start'])
async def command_start(message):
    if not is_authorized(message.from_user.id, message.from_user.username):
        return
    welcome_text = (
        "🛡️ <b>System Daemon Active</b>\n\n"
        "Welcome, Operator. Control infrastructure is online.\n"
        "Available commands:\n"
        "/fetch — Execute asynchronous market data pipeline\n"
        "/status — Check core daemon metrics"
    )
    await bot.reply_to(message, welcome_text, parse_mode="HTML")

@bot.message_handler(commands=['status'])
async def command_status(message):
    if not is_authorized(message.from_user.id, message.from_user.username):
        return
    status_text = (
        "📊 <b>Daemon Status</b>\n"
        "• Environment: Production\n"
        f"• Target Monitored Assets: {len(MARKET_CONFIG['TARGET_SYMBOLS'])}\n"
        "• Security Filter: Active (Hardware/ID Lock)"
    )
    await bot.reply_to(message, status_text, parse_mode="HTML")

@bot.message_handler(commands=['fetch'])
async def command_fetch(message):
    if not is_authorized(message.from_user.id, message.from_user.username):
        return
    
    status_msg = await bot.reply_to(message, "🔄 Connecting to API infrastructure, please wait...")
    
    import aiohttp
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_symbol_price(session, symbol) for symbol in MARKET_CONFIG["TARGET_SYMBOLS"]]
        results = await asyncio.gather(*tasks)
        cleaned_data = [res for res in results if res is not None]

    if not cleaned_data:
        await bot.edit_message_text(
            "❌ Data pipeline execution failed. Check server logs.", 
            message.chat.id, 
            status_msg.message_id
        )
        return

    report = "📋 <b>Market Pipeline Report</b>\n\n"
    for record in cleaned_data:
        report += f"• <code>{record['symbol']}</code>: <b>{record['price']}</b>\n"
    report += "\n✅ Processed successfully."
    
    await bot.delete_message(message.chat.id, status_msg.message_id)
    await bot.send_message(message.chat.id, report, parse_mode="HTML")

async def main_bot():
    if not TOKEN or not ADMIN_IDS:
        logger.critical("Configuration missing in .env file. Process terminated.")
        return
    
    logger.info("Starting Telegram control daemon via AsyncTeleBot...")
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.polling(non_stop=True)

if __name__ == "__main__":
    try:
        asyncio.run(main_bot())
    except KeyboardInterrupt:
        logger.info("Daemon stopped by administrator.")
