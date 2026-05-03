from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from config import ALLOWED_USERS, ONLY_ALLOWED_USERS
from database.db import db


class WhitelistMiddleware(BaseMiddleware):
    """
    Middleware для белого списка пользователей
    Только разрешенные пользователи могут использовать бота
    """

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id

        if user_id in ADMIN_IDS:
            return await handler(event, data)

        if not ONLY_ALLOWED_USERS:
            return await handler(event, data)

        # Проверяем белый список
        if user_id in ALLOWED_USERS:
            return await handler(event, data)

        # Проверяем в БД (если там хранятся разрешенные)
        user = db.get_user(user_id)
        if user and user.get('is_allowed', False):
            return await handler(event, data)

        # Доступ запрещён
        await event.answer("⛔ У вас нет доступа к этому боту")
        return