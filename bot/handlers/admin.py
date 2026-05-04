from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import db
from keyboards.admin_menu import get_admin_menu, get_users_list_menu, get_user_actions_menu
from keyboards.main_menu import get_main_menu
from locales import get_text
from config import ADMIN_IDS, ADMIN_SECRET
from video_cleaner.cleaner import cleanup_all_temp, cleaner

router = Router()
admin_sessions = set()


class AdminStates(StatesGroup):
    waiting_secret = State()
    waiting_broadcast_text = State()
    waiting_broadcast_photo = State()
    waiting_ban_id = State()
    waiting_unban_id = State()
    waiting_ban_all_confirm = State()
    waiting_user_message = State()


# ---------- Вход в админку ----------
@router.message(Command("admin"))
async def admin_login(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        await message.answer("⛔ Доступ запрещен")
        return
    await state.set_state(AdminStates.waiting_secret)
    await message.answer("🔐 Введите секретный код:")


@router.message(AdminStates.waiting_secret)
async def check_admin_secret(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    if message.text == ADMIN_SECRET:
        admin_sessions.add(user_id)
        await state.clear()
        await message.answer(
            "👑 Добро пожаловать в админ-панель!\n\nЗдесь вы можете управлять ботом.",
            reply_markup=get_admin_menu(lang)
        )
    else:
        await message.answer("❌ Неверный код! Доступ запрещен.")


# ---------- Выход и навигация ----------
@router.callback_query(F.data == "admin_logout")
async def admin_logout(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещен")
        return
    if user_id in admin_sessions:
        admin_sessions.remove(user_id)
    lang = await db.get_user_language(user_id)
    await callback.message.delete()
    await callback.message.answer(
        "🚪 Вы вышли из админ-панели.\n\nЧтобы войти снова, напишите /admin",
        reply_markup=get_main_menu(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "admin_back")
async def admin_back(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in ADMIN_IDS or user_id not in admin_sessions:
        await callback.answer("⛔ Доступ запрещен. Войдите заново через /admin")
        return
    lang = await db.get_user_language(user_id)
    await callback.message.delete()
    await callback.message.answer(
        "👑 Админ-панель",
        reply_markup=get_admin_menu(lang)
    )
    await callback.answer()


# ---------- Статистика ----------
@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in ADMIN_IDS or user_id not in admin_sessions:
        await callback.answer("⛔ Доступ запрещен")
        return
    total_users = await db.count_users()
    users_list = await db.get_all_users()
    active_users = len([u for u in users_list if not u.get("is_banned", False)])
    banned_users = total_users - active_users
    files_info = cleaner.get_files_info()
    total_files_size = sum(f['size_mb'] for f in files_info)
    stats_text = (
        f"📊 **Статистика бота**\n\n"
        f"👥 **Пользователи:**\n"
        f"├ Всего: {total_users}\n"
        f"├ Активных: {active_users}\n"
        f"└ Забаненных: {banned_users}\n\n"
        f"💾 **Файлы:**\n"
        f"├ Временных файлов: {len(files_info)}\n"
        f"└ Общий размер: {total_files_size:.2f} MB"
    )
    await callback.message.answer(stats_text)
    await callback.answer()


# ---------- Список пользователей ----------
@router.callback_query(F.data == "admin_users_list")
async def admin_users_list(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in ADMIN_IDS or user_id not in admin_sessions:
        await callback.answer("⛔ Доступ запрещен")
        return
    users = await db.get_all_users()
    lang = await db.get_user_language(user_id)
    if not users:
        await callback.message.answer("📭 Нет пользователей")
        return
    await callback.message.delete()
    await callback.message.answer(
        f"📋 **Список пользователей** (всего: {len(users)})\n\n"
        f"🟢 - активный | 🔴 - забанен",
        reply_markup=get_users_list_menu(users, 0, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_users_page_"))
async def admin_users_page(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in ADMIN_IDS or user_id not in admin_sessions:
        await callback.answer("⛔ Доступ запрещен")
        return
    page = int(callback.data.split("_")[-1])
    users = await db.get_all_users()
    lang = await db.get_user_language(user_id)
    await callback.message.edit_reply_markup(
        reply_markup=get_users_list_menu(users, page, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_user_"))
async def admin_user_action(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in ADMIN_IDS or user_id not in admin_sessions:
        await callback.answer("⛔ Доступ запрещен")
        return
    target_user_id = int(callback.data.split("_")[-1])
    target_user = await db.get_user(target_user_id)
    if not target_user:
        await callback.answer("❌ Пользователь не найден")
        return
    lang = await db.get_user_language(user_id)
    user_info = (
        f"👤 **Информация о пользователе**\n\n"
        f"🆔 ID: `{target_user.get('user_id')}`\n"
        f"📝 Имя: {target_user.get('first_name') or 'Нет'}\n"
        f"🔤 Username: @{target_user.get('username') or 'Нет'}\n"
        f"🌐 Язык: {target_user.get('language')}\n"
        f"🔒 Статус: {'🔴 Забанен' if target_user.get('is_banned') else '🟢 Активен'}\n"
        f"📅 Зарегистрирован: {target_user.get('created_at')}"
    )
    await callback.message.delete()
    await callback.message.answer(
        user_info,
        reply_markup=get_user_actions_menu(target_user_id, target_user.get('is_banned', False), lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_user_ban_"))
async def admin_user_ban(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in ADMIN_IDS or user_id not in admin_sessions:
        await callback.answer("⛔ Доступ запрещен")
        return
    target_user_id = int(callback.data.split("_")[-1])
    await db.ban_user(target_user_id)
    await callback.answer("✅ Пользователь забанен")
    target_user = await db.get_user(target_user_id)
    lang = await db.get_user_language(user_id)
    await callback.message.edit_reply_markup(
        reply_markup=get_user_actions_menu(target_user_id, target_user.get('is_banned', False), lang)
    )


@router.callback_query(F.data.startswith("admin_user_unban_"))
async def admin_user_unban(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in ADMIN_IDS or user_id not in admin_sessions:
        await callback.answer("⛔ Доступ запрещен")
        return
    target_user_id = int(callback.data.split("_")[-1])
    await db.unban_user(target_user_id)
    await callback.answer("✅ Пользователь разбанен")
    target_user = await db.get_user(target_user_id)
    lang = await db.get_user_language(user_id)
    await callback.message.edit_reply_markup(
        reply_markup=get_user_actions_menu(target_user_id, target_user.get('is_banned', False), lang)
    )


@router.callback_query(F.data.startswith("admin_user_msg_"))
async def admin_user_msg(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if user_id not in ADMIN_IDS or user_id not in admin_sessions:
        await callback.answer("⛔ Доступ запрещен")
        return
    target_user_id = int(callback.data.split("_")[-1])
    await state.update_data(target_user_id=target_user_id)
    await state.set_state(AdminStates.waiting_user_message)
    await callback.message.answer(
        f"✏️ Введите сообщение для пользователя {target_user_id}:\n\n"
        f"(можно отправлять текст, фото, видео)"
    )
    await callback.answer()


@router.message(AdminStates.waiting_user_message)
async def send_user_message(message: types.Message, state: FSMContext):
    admin_id = message.from_user.id
    if admin_id not in ADMIN_IDS or admin_id not in admin_sessions:
        return
    data = await state.get_data()
    target_user_id = data.get('target_user_id')
    try:
        if message.text:
            await message.bot.send_message(target_user_id, f"📩 Сообщение от администратора:\n\n{message.text}")
        elif message.photo:
            await message.bot.send_photo(target_user_id, message.photo[-1].file_id,
                                         caption=f"📩 Сообщение от администратора:\n\n{message.caption or ''}")
        elif message.video:
            await message.bot.send_video(target_user_id, message.video.file_id,
                                         caption=f"📩 Сообщение от администратора:\n\n{message.caption or ''}")
        else:
            await message.answer("❌ Неподдерживаемый тип сообщения")
            return
        await message.answer("✅ Сообщение отправлено пользователю")
    except Exception as e:
        await message.answer(f"❌ Ошибка отправки: {e}")
    await state.clear()


@router.callback_query(F.data == "admin_back_to_list")
async def admin_back_to_list(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in ADMIN_IDS or user_id not in admin_sessions:
        await callback.answer("⛔ Доступ запрещен")
        return
    users = await db.get_all_users()
    lang = await db.get_user_language(user_id)
    await callback.message.delete()
    await callback.message.answer(
        f"📋 **Список пользователей** (всего: {len(users)})",
        reply_markup=get_users_list_menu(users, 0, lang)
    )
    await callback.answer()


@router.callback_query(F.data == "admin_clean_files")
async def admin_clean_files(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in ADMIN_IDS or user_id not in admin_sessions:
        await callback.answer("⛔ Доступ запрещен")
        return
    deleted = cleanup_all_temp()
    await callback.message.answer(f"🗑️ Удалено {deleted} временных файлов")
    await callback.answer()


@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if user_id not in ADMIN_IDS or user_id not in admin_sessions:
        await callback.answer("⛔ Доступ запрещен")
        return
    await state.set_state(AdminStates.waiting_broadcast_text)
    await callback.message.answer(
        "📢 **Рассылка**\n\n"
        "Отправьте текст или текст + фото для рассылки всем пользователям.\n"
        "Для отмены напишите /cancel"
    )
    await callback.answer()


@router.message(AdminStates.waiting_broadcast_text)
async def process_broadcast(message: types.Message, state: FSMContext):
    admin_id = message.from_user.id
    if admin_id not in ADMIN_IDS or admin_id not in admin_sessions:
        return
    users = await db.get_all_users()
    sent = 0
    failed = 0
    status_msg = await message.answer("📢 Начинаю рассылку...")
    for user in users:
        if user.get("is_banned"):
            continue
        try:
            if message.photo:
                await message.bot.send_photo(
                    chat_id=user["user_id"],
                    photo=message.photo[-1].file_id,
                    caption=message.caption or "📢 Рассылка"
                )
            elif message.text:
                await message.bot.send_message(
                    chat_id=user["user_id"],
                    text=f"📢 {message.text}"
                )
            sent += 1
        except:
            failed += 1
        import asyncio
        await asyncio.sleep(0.05)
    await status_msg.edit_text(
        f"✅ Рассылка завершена!\n\n"
        f"📤 Отправлено: {sent}\n"
        f"❌ Не доставлено: {failed}"
    )
    await state.clear()


@router.message(Command("cancel"))
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("✅ Действие отменено")


@router.callback_query(F.data == "admin_ban_all")
async def admin_ban_all(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if user_id not in ADMIN_IDS or user_id not in admin_sessions:
        await callback.answer("⛔ Доступ запрещен")
        return
    await state.set_state(AdminStates.waiting_ban_all_confirm)
    await callback.message.answer(
        "⚠️ **ВНИМАНИЕ!** ⚠️\n\n"
        "Вы собираетесь забанить ВСЕХ пользователей.\n"
        "Это действие необратимо.\n\n"
        "Для подтверждения напишите: **ПОДТВЕРЖДАЮ**"
    )
    await callback.answer()


@router.message(AdminStates.waiting_ban_all_confirm)
async def process_ban_all(message: types.Message, state: FSMContext):
    admin_id = message.from_user.id
    if admin_id not in ADMIN_IDS or admin_id not in admin_sessions:
        return
    if message.text == "ПОДТВЕРЖДАЮ":
        await db.ban_all_users()
        await message.answer("⚠️ ВСЕ пользователи забанены")
    else:
        await message.answer("❌ Бан всех отменен")
    await state.clear()


@router.callback_query(F.data == "admin_ban")
async def admin_ban(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if user_id not in ADMIN_IDS or user_id not in admin_sessions:
        await callback.answer("⛔ Доступ запрещен")
        return
    await state.set_state(AdminStates.waiting_ban_id)
    await callback.message.answer("🆔 Введите ID пользователя для бана:")
    await callback.answer()


@router.message(AdminStates.waiting_ban_id)
async def process_ban(message: types.Message, state: FSMContext):
    admin_id = message.from_user.id
    if admin_id not in ADMIN_IDS or admin_id not in admin_sessions:
        return
    try:
        user_id_to_ban = int(message.text)
        await db.ban_user(user_id_to_ban)
        await message.answer(f"✅ Пользователь {user_id_to_ban} забанен")
    except:
        await message.answer("❌ Неверный ID")
    await state.clear()


@router.callback_query(F.data == "admin_unban")
async def admin_unban(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if user_id not in ADMIN_IDS or user_id not in admin_sessions:
        await callback.answer("⛔ Доступ запрещен")
        return
    await state.set_state(AdminStates.waiting_unban_id)
    await callback.message.answer("🆔 Введите ID пользователя для разбана:")
    await callback.answer()


@router.message(AdminStates.waiting_unban_id)
async def process_unban(message: types.Message, state: FSMContext):
    admin_id = message.from_user.id
    if admin_id not in ADMIN_IDS or admin_id not in admin_sessions:
        return
    try:
        user_id_to_unban = int(message.text)
        await db.unban_user(user_id_to_unban)
        await message.answer(f"✅ Пользователь {user_id_to_unban} разбанен")
    except:
        await message.answer("❌ Неверный ID")
    await state.clear()