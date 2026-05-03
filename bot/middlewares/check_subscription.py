from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from database.db import db
from utils.subscription import check_subscription
from config import ADMIN_IDS
from keyboards.main_menu import get_subscribe_menu
from locales import get_text


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id

        # Получаем пользователя из БД (асинхронно)
        user = await db.get_user(user_id)

        # Проверяем бан (user — словарь или None)
        if user and user.get("is_banned"):
            await event.answer("⛔ Вы забанены")
            return

        # Админов не проверяем на подписку
        if user_id in ADMIN_IDS:
            return await handler(event, data)

        # Проверяем подписку
        bot = data.get('bot')
        is_subscribed = await check_subscription(bot, user_id)

        if not is_subscribed:
            lang = await db.get_user_language(user_id)
            await event.answer(
                get_text(lang, 'subscribe_required'),
                reply_markup=get_subscribe_menu(lang)
            )
            return

        return await handler(event, data)