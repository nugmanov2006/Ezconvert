from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_settings_language_menu(lang: str) -> ReplyKeyboardMarkup:
    """Меню настроек с выбором языка"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇬🇧 English")],
            [KeyboardButton(text="◀️ Назад")]
        ],
        resize_keyboard=True
    )