from aiogram import Router, types, F
from database.db import db
from keyboards.main_menu import get_main_menu
from keyboards.settings_menu import get_settings_language_menu
from locales import get_text

router = Router()


@router.message(F.text.in_([get_text('ru', 'btn_settings'), get_text('en', 'btn_settings')]))
async def settings_menu(message: types.Message):
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)

    await message.answer(
        "⚙️ **Настройки**\n\nВыберите язык:",
        parse_mode="Markdown",
        reply_markup=get_settings_language_menu(lang)
    )


@router.message(F.text == "🇷🇺 Русский")
async def set_language_ru(message: types.Message):
    user_id = message.from_user.id
    await db.set_language(user_id, "ru")

    await message.answer(
        "✅ Язык изменен на русский",
        reply_markup=get_main_menu("ru")
    )


@router.message(F.text == "🇬🇧 English")
async def set_language_en(message: types.Message):
    user_id = message.from_user.id
    await db.set_language(user_id, "en")

    await message.answer(
        "✅ Language changed to English",
        reply_markup=get_main_menu("en")
    )


@router.message(F.text == "◀️ Назад")
async def back_to_main(message: types.Message):
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)

    await message.answer(
        get_text(lang, 'start'),
        reply_markup=get_main_menu(lang)
    )