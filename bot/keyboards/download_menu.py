from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from locales import get_text


def get_download_platform_menu(lang: str) -> InlineKeyboardMarkup:
    """Меню выбора платформы для скачивания"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, 'platform_youtube'), callback_data="download_youtube")],
        [InlineKeyboardButton(text=get_text(lang, 'platform_tiktok'), callback_data="download_tiktok")],
        [InlineKeyboardButton(text=get_text(lang, 'platform_instagram'), callback_data="download_instagram")],
        [InlineKeyboardButton(text=get_text(lang, 'platform_back'), callback_data="back_to_main")]
    ])


def get_download_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """Клавиатура для главного меню с кнопкой скачивания"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, 'btn_convert')),
             KeyboardButton(text=get_text(lang, 'btn_download'))],
            [KeyboardButton(text=get_text(lang, 'btn_settings'))]
        ],
        resize_keyboard=True
    )