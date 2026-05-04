import os
import uuid
from aiogram import Router, types, F
from aiogram.types import BufferedInputFile
from database.db import db
from locales import get_text
from utils.audio_converter import audio_converter
from video_cleaner.cleaner import schedule_delete_after_delay

router = Router()


# ===== КОНВЕРТАЦИЯ АУДИО → ГОЛОСОВОЕ =====
@router.message(F.text.in_([get_text('ru', 'btn_convert_audio'), get_text('en', 'btn_convert_audio')]))
async def ask_audio(message: types.Message):
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    await message.answer(get_text(lang, 'send_audio'))


@router.message(F.audio)
async def handle_audio(message: types.Message, bot):
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    audio = message.audio

    filename = audio.file_name or "audio.mp3"
    if not audio_converter.is_supported_format(filename):
        await message.answer(get_text(lang, 'unsupported_audio'))
        return

    if audio.file_size > 50 * 1024 * 1024:
        await message.answer(get_text(lang, 'file_too_big'))
        return

    await bot.send_chat_action(chat_id=user_id, action="record_voice")
    status_msg = await message.answer(get_text(lang, 'converting_audio'))

    unique_id = str(uuid.uuid4())[:8]
    input_path = f"temp_audio_{user_id}_{unique_id}.{filename.split('.')[-1]}"
    output_path = f"voice_{user_id}_{unique_id}.ogg"

    try:
        file = await bot.get_file(audio.file_id)
        await bot.download_file(file.file_path, input_path)

        success, error = await audio_converter.convert_to_voice(input_path, output_path)

        if not success:
            await status_msg.edit_text(get_text(lang, 'audio_conversion_error', error=error))
            return

        await bot.send_chat_action(chat_id=user_id, action="upload_voice")

        with open(output_path, 'rb') as f:
            await bot.send_voice(
                chat_id=user_id,
                voice=BufferedInputFile(f.read(), filename="voice.ogg"),
                caption=get_text(lang, 'audio_conversion_success')
            )

        await status_msg.delete()

        await db.add_video(user_id, audio.file_id, output_path, os.path.getsize(output_path))
        schedule_delete_after_delay(input_path, seconds=30)
        schedule_delete_after_delay(output_path, seconds=30)

    except Exception as e:
        await status_msg.edit_text(get_text(lang, 'audio_conversion_error', error=str(e)))
        for path in [input_path, output_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass


# ===== КОНВЕРТАЦИЯ ГОЛОСОВОГО → АУДИО =====
@router.message(F.text.in_([get_text('ru', 'btn_voice_to_audio'), get_text('en', 'btn_voice_to_audio')]))
async def ask_voice_for_convert(message: types.Message):
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    await message.answer(get_text(lang, 'send_voice_for_convert'))


@router.message(F.voice)
async def handle_voice_to_audio(message: types.Message, bot):
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    voice = message.voice

    if voice.file_size > 50 * 1024 * 1024:
        await message.answer(get_text(lang, 'file_too_big'))
        return

    await bot.send_chat_action(chat_id=user_id, action="upload_audio")
    status_msg = await message.answer(get_text(lang, 'converting_voice'))

    unique_id = str(uuid.uuid4())[:8]
    input_path = f"temp_voice_{user_id}_{unique_id}.ogg"
    output_path = f"audio_{user_id}_{unique_id}.mp3"

    try:
        file = await bot.get_file(voice.file_id)
        await bot.download_file(file.file_path, input_path)
        print(f"✅ Скачано голосовое: {input_path}")

        success, error = await audio_converter.convert_voice_to_audio(input_path, output_path)

        if not success:
            await status_msg.edit_text(get_text(lang, 'voice_conversion_error', error=error))
            return

        with open(output_path, 'rb') as f:
            await bot.send_audio(
                chat_id=user_id,
                audio=BufferedInputFile(f.read(), filename=f"audio_{unique_id}.mp3"),
                caption=get_text(lang, 'voice_conversion_success')
            )

        await status_msg.delete()

        await db.add_video(user_id, voice.file_id, output_path, os.path.getsize(output_path))
        schedule_delete_after_delay(input_path, seconds=30)
        schedule_delete_after_delay(output_path, seconds=30)

    except Exception as e:
        await status_msg.edit_text(get_text(lang, 'voice_conversion_error', error=str(e)))
        print(f"❌ Ошибка конвертации голосового: {e}")
        for path in [input_path, output_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass