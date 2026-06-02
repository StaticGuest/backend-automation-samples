import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher, html
from aiogram.filters import Command, BaseFilter
from aiogram.types import Message
from dotenv import load_dotenv

# Імпортуємо логіку з нашого першого модуля (потрібно трохи адаптувати main.py)
from main import fetch_symbol_price, CONFIG as MARKET_CONFIG

# Завантажуємо змінні оточення з файлу .env
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Очікуємо рядок з ID через кому, наприклад: 12345678,98765432
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("TelegramDaemon")

# Кастомний фільтр для безпеки (Cybersecurity Layer)
class AdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        is_admin = message.from_user.id in ADMIN_IDS
        if not is_admin:
            logger.warning(
                f"Unauthorized access attempt by ID {message.from_user.id} "
                f"(@{message.from_user.username})"
            )
        return is_admin

dp = Dispatcher()

@dp.message(Command("start"), AdminFilter())
async def command_start_handler(message: Message) -> None:
    """Обробка команди /start для авторизованих адмінів."""
    welcome_text = (
        f"🛡️ {html.bold('System Daemon Active')}\n\n"
        f"Welcome, Operator. Control infrastructure is online.\n"
        f"Available commands:\n"
        f"/fetch — Execute asynchronous market data pipeline\n"
        f"/status — Check core daemon metrics"
    )
    await message.answer(welcome_text, parse_mode="HTML")

@dp.message(Command("status"), AdminFilter())
async def command_status_handler(message: Message) -> None:
    """Перевірка статусу системи."""
    status_text = (
        f"📊 {html.bold('Daemon Status')}\n"
        f"• Environment: Production\n"
        f"• Target Monitored Assets: {len(MARKET_CONFIG['TARGET_SYMBOLS'])}\n"
        f"• Security Filter: Active (Hardware/ID Lock)"
    )
    await message.answer(status_text, parse_mode="HTML")

@dp.message(Command("fetch"), AdminFilter())
async def command_fetch_handler(message: Message) -> None:
    """
    Інтеграційний воркфлоу: бот викликає асинхронний пайплайн з main.py
    і відправляє структурований звіт користувачу в чат.
    """
    status_msg = await message.answer("🔄 Connecting to API infrastructure, please wait...")
    
    import aiohttp
    async with aiohttp.ClientSession() as session:
        # Запускаємо збір даних паралельно
        tasks = [fetch_symbol_price(session, symbol) for symbol in MARKET_CONFIG["TARGET_SYMBOLS"]]
        results = await asyncio.gather(*tasks)
        cleaned_data = [res for res in results if res is not None]

    if not cleaned_data:
        await status_msg.edit_text("❌ Data pipeline execution failed. Check server logs.")
        return

    # Формуємо красивий звіт для клієнта
    report = f"📋 {html.bold('Market Pipeline Report')}\n\n"
    for record in cleaned_data:
        report += f"• {html.code(record['symbol'])}: {html.bold(record['price'])}\n"
    
    report += f"\n✅ Processed successfully."
    
    await status_msg.delete()
    await message.answer(report, parse_mode="HTML")

# Заглушка для неавторизованих користувачів (система мовчить або відшиває)
@dp.message(~AdminFilter())
async def unauthorized_handler(message: Message) -> None:
    # З міркувань безпеки краще взагалі ігнорувати або видавати нейтральну помилку
    pass

async def main_bot():
    if not TOKEN:
        logger.critical("TELEGRAM_BOT_TOKEN is missing in environment variables. Process terminated.")
        return
    if not ADMIN_IDS:
        logger.critical("ADMIN_IDS registry is empty. Protection filter will block everyone. Process terminated.")
        return

    bot = Bot(token=TOKEN)
    logger.info("Starting Telegram control daemon...")
    # Запускаємо лонг-полінг без обробки старих повідомлень (clean start)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main_bot())
    except KeyboardInterrupt:
        logger.info("Daemon stopped by administrator.")