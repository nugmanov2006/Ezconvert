import os
import uuid
import asyncio
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile
from database.db import db
from locales import get_text
from utils.video_downloader import downloader
from video_cleaner.cleaner import schedule_delete_after_delay

router = Router()


class DownloadStates(StatesGroup):
    waiting_url = State()


async def show_progress(status_msg: types.Message, platform: str):
    """Простая анимация загрузки"""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    step = 0

    while True:
        frame = frames[step % len(frames)]
        await status_msg.edit_text(
            f"{frame} **Скачивание с {platform.upper()}**\n\n"
            f"_Подождите, видео обрабатывается..._",
            parse_mode="Markdown"
        )
        step += 1
        await asyncio.sleep(0.15)


@router.message(F.text.in_([get_text('ru', 'btn_download'), get_text('en', 'btn_download')]))
async def download_menu(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    await state.set_state(DownloadStates.waiting_url)
    await message.answer(get_text(lang, 'send_link'))


@router.message(DownloadStates.waiting_url)
async def download_video(message: types.Message, state: FSMContext, bot):
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    url = message.text.strip()

    platform = downloader.detect_platform(url)

    if not platform:
        await message.answer(get_text(lang, 'unsupported_url'))
        return

    status_msg = await message.answer(f"🔄 **Скачивание с {platform.upper()}...**")

    # Запускаем анимацию
    animation_task = asyncio.create_task(show_progress(status_msg, platform))

    try:
        filepath, platform_name = await downloader.download_video(url, platform)

        animation_task.cancel()

        if not filepath or not os.path.exists(filepath):
            await status_msg.edit_text(f"❌ Не удалось скачать видео с {platform.upper()}")
            return

        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)

        if file_size_mb > 50:
            await status_msg.edit_text(f"❌ Видео слишком большое ({file_size_mb:.1f} MB)")
            os.remove(filepath)
            return

        await status_msg.edit_text("📤 Отправляю видео...")

        with open(filepath, 'rb') as f:
            await bot.send_video(
                chat_id=user_id,
                video=BufferedInputFile(f.read(), filename=f"video_{uuid.uuid4().hex[:8]}.mp4"),
                caption=f"✅ **Скачано с {platform_name}**\n📊 **Размер:** {file_size_mb:.1f} MB",
                parse_mode="Markdown"
            )

        await status_msg.delete()

        await db.add_video(user_id, url, filepath, int(file_size_mb * 1024 * 1024))
        schedule_delete_after_delay(filepath, seconds=30)

    except asyncio.CancelledError:
        pass
    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка: {str(e)[:100]}")
        print(f"Download error: {e}")

    finally:
        await state.clear()