from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command  # Новый путь для фильтров
import asyncio
import aiosqlite

# Telegram bot token
BOT_TOKEN = "YOUR_BOT_TOKEN"

# Создание экземпляров бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Путь к базе данных
DB_PATH = "bot_data.db"


# Инициализация базы данных
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                chat_id INTEGER,
                message TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY,
                random_replies_enabled BOOLEAN DEFAULT 0
            )
        """)
        await db.execute("INSERT OR IGNORE INTO settings (id) VALUES (1)")
        await db.commit()


# Обработчик команды /start
@dp.message(Command(commands=["start"]))
async def start_handler(message: Message):
    await message.reply("Привет! Я готов работать.")


# Обработчик любых сообщений
@dp.message()
async def log_message(message: Message):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO messages (user_id, username, chat_id, message)
            VALUES (?, ?, ?, ?)
        """, (message.from_user.id, message.from_user.username, message.chat.id, message.text))
        await db.commit()

    # Проверяем, включены ли случайные ответы
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT random_replies_enabled FROM settings WHERE id = 1")
        enabled = (await cursor.fetchone())[0]

    if enabled:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("SELECT message FROM messages ORDER BY RANDOM() LIMIT 1")
            random_message = (await cursor.fetchone())[0]
            await message.reply(random_message)


# Основная функция
async def main():
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
