from aiogram import Bot
from config import CHANNEL_USERNAME, CHANNEL_ID


async def check_subscription(bot: Bot, user_id: int) -> bool:
    """Проверяет подписку пользователя на канал"""
    try:
        # Пробуем через username
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)

        # Статусы: creator, administrator, member - подписан
        return member.status in ['creator', 'administrator', 'member']
    except Exception:
        # Если ошибка, пробуем через ID канала
        try:
            member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
            return member.status in ['creator', 'administrator', 'member']
        except:
            return False