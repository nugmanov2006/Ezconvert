from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from locales import get_text


def get_admin_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="🚫 Забанить пользователя", callback_data="admin_ban")],
        [InlineKeyboardButton(text="✅ Разбанить пользователя", callback_data="admin_unban")],
        [InlineKeyboardButton(text="⚠️ Бан всех пользователей", callback_data="admin_ban_all")],
        [InlineKeyboardButton(text="📁 Список пользователей", callback_data="admin_users_list")],
        [InlineKeyboardButton(text="🗑️ Очистить временные файлы", callback_data="admin_clean_files")],
        [InlineKeyboardButton(text="🚪 Выйти из админки", callback_data="admin_logout")]
    ])


def get_admin_back_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад в админку", callback_data="admin_back")]
    ])


def get_users_list_menu(users: list, page: int = 0, lang: str = "ru") -> InlineKeyboardMarkup:
    keyboard = []
    start_idx = page * 5
    end_idx = start_idx + 5
    page_users = users[start_idx:end_idx]

    for user in page_users:
        if hasattr(user, 'is_banned'):  # объект
            status = "🔴" if user.is_banned else "🟢"
            name = (user.first_name or str(user.user_id))[:20]
            user_id = user.user_id
        else:  # словарь
            status = "🔴" if user.get('is_banned') else "🟢"
            name = (user.get('first_name') or str(user.get('user_id')))[:20]
            user_id = user.get('user_id')

        keyboard.append([InlineKeyboardButton(
            text=f"{status} {name} ({user_id})",
            callback_data=f"admin_user_{user_id}"
        )])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"admin_users_page_{page-1}"))
    if end_idx < len(users):
        nav_buttons.append(InlineKeyboardButton(text="Вперед ▶️", callback_data=f"admin_users_page_{page+1}"))

    if nav_buttons:
        keyboard.append(nav_buttons)

    keyboard.append([InlineKeyboardButton(text="◀️ В админку", callback_data="admin_back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_user_actions_menu(user_id: int, is_banned: bool, lang: str) -> InlineKeyboardMarkup:
    ban_text = "✅ Разбанить" if is_banned else "🚫 Забанить"
    ban_data = f"admin_user_unban_{user_id}" if is_banned else f"admin_user_ban_{user_id}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=ban_text, callback_data=ban_data)],
        [InlineKeyboardButton(text="💬 Написать пользователю", callback_data=f"admin_user_msg_{user_id}")],
        [InlineKeyboardButton(text="◀️ Назад к списку", callback_data="admin_back_to_list")]
    ])