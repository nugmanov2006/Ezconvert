from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from locales import get_text

def get_main_menu(lang: str) -> ReplyKeyboardMarkup:
    """Главное меню с двумя кнопками в ряд"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=get_text(lang, 'btn_convert')),
             KeyboardButton(text=get_text(lang, 'btn_download'))],
            [
                KeyboardButton(text=get_text(lang, 'btn_convert_audio')),
             KeyboardButton(text=get_text(lang, 'btn_voice_to_audio'))],  # ← новая кнопка
            [
                KeyboardButton(text=get_text(lang, 'btn_settings'))]

        ],
        resize_keyboard=True
    )


def get_subscribe_menu(lang: str) -> ReplyKeyboardMarkup:
    """Клавиатура для проверки подписки"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, 'btn_check_subscription'))]
        ],
        resize_keyboard=True,
        input_field_placeholder="Подпишитесь на канал"
    )