import os
from dotenv import load_dotenv

load_dotenv()

# ========== ЗАЩИТА ==========
RATE_LIMIT = 1.0
ALLOWED_USERS = [123456789]          # Замените на ваш ID, если нужен белый список
ONLY_ALLOWED_USERS = False
MAX_FILE_SIZE_MB = 50
REQUEST_TIMEOUT = 30
CONNECTION_TIMEOUT = 15

# ========== ОСНОВНЫЕ НАСТРОЙКИ ==========
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_SECRET = "admin123"
CHANNEL_USERNAME = "@photorusta"
CHANNEL_ID = -1003068825899
ADMIN_IDS = [7595806386]             # Ваш Telegram ID

# ========== ПРОКСИ ОТКЛЮЧЁН (для сервера в ЕС) ==========
PROXY_URL = ""

# ========== НАСТРОЙКИ КОНВЕРТАЦИИ ==========
MAX_VIDEO_SIZE = 50 * 1024 * 1024
CIRCLE_MAX_SIZE = 10 * 1024 * 1024


