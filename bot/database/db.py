import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from bson import ObjectId
import motor.motor_asyncio
from config import MONGO_URL

# Подключение к MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.bot_db  # база данных bot_db
users_collection = db.users
videos_collection = db.videos


# ========== ПОЛЬЗОВАТЕЛИ ==========

async def add_user(user_id: int, username: str = None, first_name: str = None, last_name: str = None):
    """Добавить или обновить пользователя"""
    await users_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "last_active": datetime.now()
            },
            "$setOnInsert": {
                "language": "ru",
                "is_banned": False,
                "is_admin": False,
                "created_at": datetime.now()
            }
        },
        upsert=True
    )


async def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Получить пользователя по ID"""
    return await users_collection.find_one({"user_id": user_id})


async def set_language(user_id: int, language: str):
    """Установить язык пользователя"""
    await users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"language": language}}
    )


async def get_user_language(user_id: int) -> str:
    """Получить язык пользователя"""
    user = await get_user(user_id)
    return user.get("language", "ru") if user else "ru"


async def ban_user(user_id: int):
    """Забанить пользователя"""
    await users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"is_banned": True}}
    )


async def unban_user(user_id: int):
    """Разбанить пользователя"""
    await users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"is_banned": False}}
    )


async def ban_all_users():
    """Забанить всех пользователей (кроме админов)"""
    await users_collection.update_many(
        {"is_admin": False},
        {"$set": {"is_banned": True}}
    )


async def get_all_users() -> List[Dict[str, Any]]:
    """Получить всех пользователей"""
    cursor = users_collection.find({})
    return await cursor.to_list(length=None)


async def count_users() -> int:
    """Количество пользователей"""
    return await users_collection.count_documents({})


# ========== ВИДЕО ==========

async def add_video(user_id: int, original_file_id: str, converted_file_path: str, file_size: int) -> str:
    """Добавить видео в БД, возвращает ObjectId как строку"""
    result = await videos_collection.insert_one({
        "user_id": user_id,
        "original_file_id": original_file_id,
        "converted_file_path": converted_file_path,
        "file_size": file_size,
        "created_at": datetime.now(),
        "deleted_at": None
    })
    return str(result.inserted_id)


async def mark_video_deleted(video_id: str):
    """Пометить видео как удаленное по его ObjectId"""
    try:
        await videos_collection.update_one(
            {"_id": ObjectId(video_id)},
            {"$set": {"deleted_at": datetime.now()}}
        )
    except:
        pass  # если неверный формат id


async def get_old_videos(hours: int = 24) -> List[Dict[str, Any]]:
    """Получить видео старше N часов (не удалённые)"""
    threshold = datetime.now() - timedelta(hours=hours)
    cursor = videos_collection.find({
        "deleted_at": None,
        "created_at": {"$lt": threshold}
    })
    return await cursor.to_list(length=None)


# Для обратной совместимости с синхронным кодом (временно),
# но лучше везде использовать await.
class Database:
    """
    Класс-обёртка для синхронного доступа (не рекомендуется).
    Используйте прямые async функции выше.
    """
    def __init__(self, db_path=None):
        # Оставлен для совместимости, но не используется
        pass

    @staticmethod
    async def add_user(*args, **kwargs):
        return await add_user(*args, **kwargs)

    @staticmethod
    async def get_user(*args, **kwargs):
        return await get_user(*args, **kwargs)

    @staticmethod
    async def set_language(*args, **kwargs):
        return await set_language(*args, **kwargs)

    @staticmethod
    async def get_user_language(*args, **kwargs):
        return await get_user_language(*args, **kwargs)

    @staticmethod
    async def ban_user(*args, **kwargs):
        return await ban_user(*args, **kwargs)

    @staticmethod
    async def unban_user(*args, **kwargs):
        return await unban_user(*args, **kwargs)

    @staticmethod
    async def ban_all_users(*args, **kwargs):
        return await ban_all_users(*args, **kwargs)

    @staticmethod
    async def get_all_users(*args, **kwargs):
        return await get_all_users(*args, **kwargs)

    @staticmethod
    async def count_users(*args, **kwargs):
        return await count_users(*args, **kwargs)

    @staticmethod
    async def add_video(*args, **kwargs):
        return await add_video(*args, **kwargs)

    @staticmethod
    async def mark_video_deleted(*args, **kwargs):
        return await mark_video_deleted(*args, **kwargs)

    @staticmethod
    async def get_old_videos(*args, **kwargs):
        return await get_old_videos(*args, **kwargs)


# Создаём глобальный экземпляр для обратной совместимости
db = Database()