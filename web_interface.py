from flask import Flask, render_template, request, redirect, url_for
from flask_httpauth import HTTPBasicAuth
import aiosqlite
import asyncio
import os

# Инициализация Flask-приложения и авторизации
app = Flask(__name__)
auth = HTTPBasicAuth()

# Хранение логина и пароля в переменных окружения
USERNAME = os.getenv("BOT_ADMIN_USERNAME", "admin")
PASSWORD = os.getenv("BOT_ADMIN_PASSWORD", "password")

# Функция валидации пользователя
@auth.verify_password
def verify_password(username, password):
    return username == USERNAME and password == PASSWORD

# Путь к базе данных
DB_PATH = "bot_data.db"

# Асинхронная функция для получения последних 50 сообщений
async def get_last_messages(limit=50):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT user_id, username, message FROM messages ORDER BY id DESC LIMIT ?", (limit,))
        messages = await cursor.fetchall()
    return messages

@app.route("/")
@auth.login_required
async def index():
    # Получаем количество сообщений
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM messages")
        message_count = (await cursor.fetchone())[0]
        cursor = await db.execute("SELECT random_replies_enabled FROM settings WHERE id = 1")
        random_enabled = (await cursor.fetchone())[0]

    # Получаем последние 50 сообщений
    messages = await get_last_messages(50)

    # Отправляем данные на страницу
    return render_template("index.html", message_count=message_count, random_enabled=random_enabled, messages=messages)

@app.route("/toggle_random", methods=["POST"])
@auth.login_required
async def toggle_random():
    enabled = request.form.get("enabled") == "on"
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE settings SET random_replies_enabled = ? WHERE id = 1", (enabled,))
        await db.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
