import time
from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

# Хранилище последних вызовов пользователей
user_last_call: Dict[int, float] = {}


class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware для защиты от флуда (ограничение частоты запросов)
    Пользователь может отправлять не более 1 сообщения в секунду
    """

    def __init__(self, rate_limit: float = 1.0):
        """
        :param rate_limit: минимальный интервал между запросами в секундах
        """
        self.rate_limit = rate_limit

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        current_time = time.time()

        # Проверяем, когда пользователь писал в последний раз
        last_call = user_last_call.get(user_id, 0)

        if current_time - last_call < self.rate_limit:
            # Слишком часто! Игнорируем или отправляем предупреждение
            if isinstance(event, Message):
                await event.answer(
                    "⏳ Пожалуйста, не спамьте!\n"
                    f"Подождите {self.rate_limit - (current_time - last_call):.1f} секунд"
                )
            return  # Блокируем обработку

        # Обновляем время последнего вызова
        user_last_call[user_id] = current_time

        # Пропускаем к хендлеру
        return await handler(event, data)