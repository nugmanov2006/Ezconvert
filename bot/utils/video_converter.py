import os
import subprocess
import shutil




async def convert_to_video_note(input_path: str, output_path: str, max_size_mb: float = 9.5):
    """Конвертирует видео в формат видеосообщения (кружочек)"""

    # Проверяем входной файл
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Файл не найден: {input_path}")

    # Проверяем ffmpeg
    ffmpeg_path = shutil.which('ffmpeg')
    if not ffmpeg_path:
        raise RuntimeError("FFmpeg не установлен")

    size_mb = os.path.getsize(input_path) / (1024 * 1024)
    if size_mb > 50:
        raise ValueError(f"Видео слишком большое ({size_mb:.1f} MB)")

    # Настройки сжатия
    cmd = [
        ffmpeg_path,
        "-i", input_path,
        "-vf", "crop=min(iw\\,ih):min(iw\\,ih),scale=640:640",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "28",  # Хорошее сжатие
        "-c:a", "aac",
        "-b:a", "96k",
        "-ar", "44100",
        "-ac", "1",
        "-t", "60",  # Максимум 60 секунд
        "-movflags", "+faststart",
        output_path,
        "-y"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg ошибка: {result.stderr}")

        output_size_mb = os.path.getsize(output_path) / (1024 * 1024)

        # Если все еще слишком большой, сжимаем сильнее
        if output_size_mb > max_size_mb:
            cmd[cmd.index("-crf") + 1] = "32"
            subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            output_size_mb = os.path.getsize(output_path) / (1024 * 1024)

        return output_size_mb

    except subprocess.TimeoutExpired:
        raise RuntimeError("Конвертация заняла слишком много времени")
