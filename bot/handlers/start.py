from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from database.db import db
from keyboards.main_menu import get_main_menu, get_subscribe_menu
from locales import get_text
from utils.subscription import check_subscription
from config import ADMIN_IDS

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext, bot):
    user = message.from_user
    await state.clear()

    # Добавляем пользователя в БД (асинхронно)
    await db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )

    lang = await db.get_user_language(user.id)

    # Проверяем бан
    user_data = await db.get_user(user.id)
    if user_data and user_data.get("is_banned"):
        await message.answer("⛔ Вы забанены")
        return

    # Проверяем подписку
    is_subscribed = await check_subscription(bot, user.id)

    if not is_subscribed:
        # Показываем клавиатуру с кнопкой проверки
        await message.answer(
            get_text(lang, 'subscribe_required'),
            reply_markup=get_subscribe_menu(lang)
        )
        return

    # Если подписан - показываем главное меню
    await message.answer(
        get_text(lang, 'start'),
        reply_markup=get_main_menu(lang)
    )


# ✅ ИСПРАВЛЕННЫЙ обработчик кнопки "Проверить подписку"
@router.message(F.text.in_([get_text('ru', 'btn_check_subscription'), get_text('en', 'btn_check_subscription')]))
async def check_subscription_button(message: types.Message, bot):
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)

    # Отправляем сообщение "проверяю"
    checking_msg = await message.answer(get_text(lang, 'subscribe_checking'))

    # Проверяем подписку
    is_subscribed = await check_subscription(bot, user_id)

    # Удаляем сообщение о проверке
    await checking_msg.delete()

    if is_subscribed:
        # ✅ Если подписался - показываем ГЛАВНОЕ МЕНЮ и приветствие
        await message.answer(
            get_text(lang, 'subscribe_success'),
            reply_markup=get_main_menu(lang)  # ← здесь главное меню
        )
    else:
        # Если нет - оставляем кнопку проверки
        await message.answer(
            get_text(lang, 'subscribe_failed'),
            reply_markup=get_subscribe_menu(lang)
        )