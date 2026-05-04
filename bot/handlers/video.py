import os
import uuid
from aiogram import Router, types, F
from aiogram.types import BufferedInputFile
from aiogram.exceptions import TelegramBadRequest
from database.db import db
from utils.video_converter import convert_to_video_note
from locales import get_text
from config import MAX_VIDEO_SIZE
from video_cleaner.cleaner import schedule_delete_after_delay

router = Router()


@router.message(F.text.in_([get_text('ru', 'btn_convert'), get_text('en', 'btn_convert')]))
async def ask_video(message: types.Message):
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    await message.answer(get_text(lang, 'sending_gif'))


@router.message(F.video)
async def handle_video(message: types.Message, bot):
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    video = message.video

    if video.file_size > MAX_VIDEO_SIZE:
        await message.answer(get_text(lang, 'file_too_big'))
        return

    try:
        await message.delete()
    except:
        pass

    await bot.send_chat_action(chat_id=user_id, action="record_video_note")
    status_msg = await message.answer(get_text(lang, 'converting'))

    unique_id = str(uuid.uuid4())[:8]
    input_path = f"temp_video_{user_id}_{unique_id}.mp4"
    output_path = f"circle_{user_id}_{unique_id}.mp4"

    try:
        file = await bot.get_file(video.file_id)
        await bot.download_file(file.file_path, input_path)
        print(f"✅ Скачано видео: {input_path}")

        final_size = await convert_to_video_note(input_path, output_path)
        print(f"✅ Сконвертировано: {output_path} ({final_size:.2f} MB)")

        await status_msg.edit_text("🔄 Отправляю готовый кружочек...")

        with open(output_path, 'rb') as f:
            await bot.send_video_note(
                chat_id=user_id,
                video_note=BufferedInputFile(f.read(), filename="circle.mp4")
            )

        await status_msg.delete()

        await db.add_video(user_id, video.file_id, output_path, int(final_size * 1024 * 1024))

        schedule_delete_after_delay(input_path, seconds=30)
        schedule_delete_after_delay(output_path, seconds=30)

    except Exception as e:
        await status_msg.edit_text(get_text(lang, 'conversion_error', error=str(e)))
        print(f"❌ Ошибка: {e}")
        for path in [input_path, output_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass


@router.message(F.animation)
async def handle_gif(message: types.Message, bot):
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    gif = message.animation

    if gif.file_size > MAX_VIDEO_SIZE:
        await message.answer(get_text(lang, 'file_too_big'))
        return

    try:
        await message.delete()
    except:
        pass

    await bot.send_chat_action(chat_id=user_id, action="record_video_note")
    status_msg = await message.answer(get_text(lang, 'gif_detected'))

    unique_id = str(uuid.uuid4())[:8]
    input_path = f"temp_gif_{user_id}_{unique_id}.gif"
    output_path = f"circle_gif_{user_id}_{unique_id}.mp4"

    try:
        file = await bot.get_file(gif.file_id)
        await bot.download_file(file.file_path, input_path)
        print(f"✅ Скачано GIF: {input_path}")

        final_size = await convert_to_video_note(input_path, output_path)
        print(f"✅ GIF сконвертирован в кружочек: {output_path} ({final_size:.2f} MB)")

        await status_msg.edit_text("🔄 Отправляю готовый кружочек...")

        with open(output_path, 'rb') as f:
            await bot.send_video_note(
                chat_id=user_id,
                video_note=BufferedInputFile(f.read(), filename="circle.mp4")
            )

        await status_msg.delete()

        await db.add_video(user_id, gif.file_id, output_path, int(final_size * 1024 * 1024))

        schedule_delete_after_delay(input_path, seconds=30)
        schedule_delete_after_delay(output_path, seconds=30)

    except Exception as e:
        await status_msg.edit_text(get_text(lang, 'conversion_error', error=str(e)))
        print(f"❌ Ошибка конвертации GIF: {e}")
        for path in [input_path, output_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass


@router.message(F.document)
async def handle_document_gif(message: types.Message, bot):
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    document = message.document

    if document.file_name and document.file_name.lower().endswith('.gif'):
        if document.file_size > MAX_VIDEO_SIZE:
            await message.answer(get_text(lang, 'file_too_big'))
            return

        try:
            await message.delete()
        except:
            pass

        await bot.send_chat_action(chat_id=user_id, action="record_video_note")
        status_msg = await message.answer(get_text(lang, 'gif_detected'))

        unique_id = str(uuid.uuid4())[:8]
        input_path = f"temp_gif_{user_id}_{unique_id}.gif"
        output_path = f"circle_gif_{user_id}_{unique_id}.mp4"

        try:
            file = await bot.get_file(document.file_id)
            await bot.download_file(file.file_path, input_path)
            print(f"✅ Скачано GIF из документа: {input_path}")

            final_size = await convert_to_video_note(input_path, output_path)

            await status_msg.edit_text("🔄 Отправляю готовый кружочек...")

            with open(output_path, 'rb') as f:
                await bot.send_video_note(
                    chat_id=user_id,
                    video_note=BufferedInputFile(f.read(), filename="circle.mp4")
                )

            await status_msg.delete()

            await db.add_video(user_id, document.file_id, output_path, int(final_size * 1024 * 1024))

            schedule_delete_after_delay(input_path, seconds=30)
            schedule_delete_after_delay(output_path, seconds=30)

        except Exception as e:
            await status_msg.edit_text(get_text(lang, 'conversion_error', error=str(e)))
            print(f"❌ Ошибка: {e}")
            for path in [input_path, output_path]:
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except:
                        pass