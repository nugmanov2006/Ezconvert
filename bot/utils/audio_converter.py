import os
import subprocess
import shutil
from typing import Tuple, Optional


class AudioConverter:
    """Конвертер аудио и голосовых сообщений"""

    def __init__(self):
        self.supported_formats = ['.mp3', '.m4a', '.ogg', '.wav', '.aac']

    def check_ffmpeg(self) -> bool:
        """Проверяет наличие ffmpeg в системе"""
        return shutil.which('ffmpeg') is not None

    # =========================================================
    # 1. КОНВЕРТАЦИЯ АУДИО → ГОЛОСОВОЕ СООБЩЕНИЕ
    # =========================================================
    async def convert_to_voice(self, input_path: str, output_path: str) -> Tuple[bool, Optional[str]]:
        """Конвертирует аудио (MP3, M4A, WAV и т.д.) в голосовое сообщение (OGG/Opus)"""

        if not self.check_ffmpeg():
            return False, "FFmpeg не установлен"

        if not os.path.exists(input_path):
            return False, "Файл не найден"

        size_mb = os.path.getsize(input_path) / (1024 * 1024)
        if size_mb > 50:
            return False, f"Файл слишком большой ({size_mb:.1f} MB)"

        try:
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-c:a', 'libopus',
                '-b:a', '32k',
                '-ar', '24000',
                '-ac', '1',
                '-f', 'ogg',
                '-y',
                output_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                return False, f"Ошибка FFmpeg: {result.stderr[:200]}"

            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                return False, "Выходной файл не создан"

            return True, None

        except subprocess.TimeoutExpired:
            return False, "Конвертация заняла слишком много времени"
        except Exception as e:
            return False, str(e)

    # =========================================================
    # 2. КОНВЕРТАЦИЯ ГОЛОСОВОГО СООБЩЕНИЯ → АУДИО (MP3)
    # =========================================================
    async def convert_voice_to_audio(self, input_path: str, output_path: str) -> Tuple[bool, Optional[str]]:
        """Конвертирует голосовое сообщение (OGG/Opus) в MP3"""

        if not self.check_ffmpeg():
            return False, "FFmpeg не установлен"

        if not os.path.exists(input_path):
            return False, "Файл не найден"

        size_mb = os.path.getsize(input_path) / (1024 * 1024)
        if size_mb > 50:
            return False, f"Файл слишком большой ({size_mb:.1f} MB)"

        try:
            # Конвертация OGG/Opus в MP3
            cmd = [
                'ffmpeg',
                '-i', input_path,  # входной файл (.ogg)
                '-c:a', 'libmp3lame',  # кодек MP3
                '-b:a', '128k',  # битрейт 128 kbps
                '-ar', '44100',  # частота дискретизации 44.1 kHz
                '-ac', '2',  # стерео (2 канала)
                '-y',  # перезаписать если существует
                output_path  # выходной файл (.mp3)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                return False, f"Ошибка FFmpeg: {result.stderr[:200]}"

            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                return False, "Выходной файл не создан"

            return True, None

        except subprocess.TimeoutExpired:
            return False, "Конвертация заняла слишком много времени"
        except Exception as e:
            return False, str(e)

    # =========================================================
    # 3. ПРОВЕРКА ПОДДЕРЖИВАЕМЫХ ФОРМАТОВ
    # =========================================================
    def is_supported_format(self, filename: str) -> bool:
        """Проверяет, поддерживается ли формат для конвертации в голосовое"""
        ext = os.path.splitext(filename)[1].lower()
        return ext in self.supported_formats


# Создаем глобальный экземпляр
audio_converter = AudioConverter()