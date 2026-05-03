import asyncio
import os
import threading
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.bot import DefaultBotProperties
from aiohttp import web

from config import BOT_TOKEN, RATE_LIMIT, ONLY_ALLOWED_USERS, ALLOWED_USERS
from database.db import db
from handlers import start, settings, video, admin, download, audio
from middlewares.throttling import ThrottlingMiddleware
from middlewares.whitelist import WhitelistMiddleware
from middlewares.check_subscription import SubscriptionMiddleware

# ========== НАСТРОЙКА СЕССИИ (БЕЗ ПРОКСИ) ==========
session = AiohttpSession(timeout=60)

bot = Bot(
    token=BOT_TOKEN,
    session=session,
    default=DefaultBotProperties()
)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ========== ПОДКЛЮЧЕНИЕ MIDDLEWARE ==========
if RATE_LIMIT and RATE_LIMIT > 0:
    dp.message.middleware(ThrottlingMiddleware(rate_limit=RATE_LIMIT))
    dp.callback_query.middleware(ThrottlingMiddleware(rate_limit=RATE_LIMIT))
    print(f"🛡️ Защита от флуда включена (лимит: {RATE_LIMIT} сек/сообщение)")

if ONLY_ALLOWED_USERS and ALLOWED_USERS:
    dp.message.middleware(WhitelistMiddleware(allowed_users=ALLOWED_USERS))
    dp.callback_query.middleware(WhitelistMiddleware(allowed_users=ALLOWED_USERS))
    print(f"🔒 Белый список включен ({len(ALLOWED_USERS)} пользователей)")

dp.message.middleware(SubscriptionMiddleware())
dp.callback_query.middleware(SubscriptionMiddleware())

# ========== ПОДКЛЮЧЕНИЕ РОУТЕРОВ ==========
dp.include_router(start.router)
dp.include_router(audio.router)
dp.include_router(settings.router)
dp.include_router(video.router)
dp.include_router(admin.router)
dp.include_router(download.router)

# ========== ВЕБ-СЕРВЕР ДЛЯ HEALTH CHECK (RENDER) ==========
app = web.Application()

async def health(request):
    return web.Response(text="OK")

app.router.add_get("/", health)
app.router.add_get("/health", health)

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)

# ========== ОСНОВНЫЕ ФУНКЦИИ ==========
async def set_commands():
    commands = [
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="admin", description="👑 Админ панель"),
        BotCommand(command="cancel", description="❌ Отменить действие"),
    ]
    await bot.set_my_commands(commands)

async def cleanup_old_videos():
    while True:
        await asyncio.sleep(3600)
        try:
            old_videos = await db.get_old_videos(hours=1)
            for video in old_videos:
                try:
                    file_path = video.get("converted_file_path")
                    if file_path and os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"🗑️ Удалён старый файл: {file_path}")
                    await db.mark_video_deleted(str(video["_id"]))
                except Exception as e:
                    print(f"Ошибка при удалении видео {video.get('_id')}: {e}")
        except Exception as e:
            print(f"Ошибка в cleanup_old_videos: {e}")

async def main():
    print("🤖 Бот запускается...")
    # Запускаем веб-сервер health check в отдельном потоке
    threading.Thread(target=run_web, daemon=True).start()
    # Устанавливаем команды бота
    await set_commands()
    # Запускаем фоновую очистку
    asyncio.create_task(cleanup_old_videos())
    print("✅ Бот готов к работе!")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")