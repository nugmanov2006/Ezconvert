import os
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict


class VideoCleaner:
    """Класс для автоматического удаления видео после конвертации"""

    def __init__(self):
        self.files_to_delete = {}
        self.downloads_path = "downloads"
        os.makedirs(self.downloads_path, exist_ok=True)

    def schedule_deletion(self, file_path: str, seconds_delay: int = 60):
        """Запланировать удаление файла через N секунд"""
        delete_time = datetime.now() + timedelta(seconds=seconds_delay)
        self.files_to_delete[file_path] = delete_time
        print(f"📅 Файл {os.path.basename(file_path)} будет удален в {delete_time.strftime('%H:%M:%S')}")

        async def auto_cleanup(self):
            """Фоновая задача для автоматического удаления"""
            while True:
                await asyncio.sleep(5)
                now = datetime.now()
                to_remove = []

                for file_path, delete_time in self.files_to_delete.items():
                    if now >= delete_time:
                        if self.delete_file(file_path):
                            to_remove.append(file_path)

                for file_path in to_remove:
                    del self.files_to_delete[file_path]

                    def delete_file(self, file_path: str) -> bool:
                        """Удалить один файл"""
                        try:
                            if os.path.exists(file_path):
                                os.remove(file_path)
                                print(f"🗑️ Удален файл: {os.path.basename(file_path)}")
                                return True
                        except Exception as e:
                            print(f"❌ Ошибка удаления: {e}")
                        return False

                    def delete_all_temp_files(self) -> int:
                        """Удалить все временные файлы"""
                        deleted = 0
                        for file in os.listdir(''):
                            if file.startswith('temp_video_') or file.startswith('circle_'):
                                if self.delete_file(file):
                                    deleted += 1
                        return deleted

                    def cleanup_downloads_folder(self) -> int:
                        """Очистка папки downloads"""
                        if not os.path.exists(self.downloads_path):
                            return 0

                        deleted = 0
                        for file in os.listdir(self.downloads_path):
                            filepath = os.path.join(self.downloads_path, file)
                            if self.delete_file(filepath):
                                deleted += 1
                        return deleted

                    def get_files_info(self) -> List[Dict]:
                        """Получить информацию о временных файлах"""
                        files_info = []

                        # Файлы в корне
                        for file in os.listdir(''):
                            if file.startswith('temp_video_') or file.startswith('circle_'):
                                stat = os.stat(file)
                                files_info.append({
                                    'name': file,
                                    'size_mb': stat.st_size / (1024 * 1024),
                                    'created': datetime.fromtimestamp(stat.st_ctime),
                                    'path': file
                                })

                        # Файлы в папке downloads
                        if os.path.exists(self.downloads_path):
                            for file in os.listdir(self.downloads_path):
                                filepath = os.path.join(self.downloads_path, file)
                                stat = os.stat(filepath)
                                files_info.append({
                                    'name': f"downloads/{file}",
                                    'size_mb': stat.st_size / (1024 * 1024),
                                    'created': datetime.fromtimestamp(stat.st_ctime),
                                    'path': filepath
                                })

                        return files_info

    def cleanup_downloads_folder(self):
        """Очистка папки downloads"""
        downloads_path = "downloads"
        if not os.path.exists(downloads_path):
            return 0

        deleted = 0
        for file in os.listdir(downloads_path):
            filepath = os.path.join(downloads_path, file)
            if self.delete_file(filepath):
                deleted += 1
        return deleted



    def __init__(self):
        self.files_to_delete = {}

    def schedule_deletion(self, file_path: str, seconds_delay: int = 60):
        """Запланировать удаление файла через N секунд"""
        delete_time = datetime.now() + timedelta(seconds=seconds_delay)
        self.files_to_delete[file_path] = delete_time
        print(f"📅 Файл будет удален в {delete_time.strftime('%H:%M:%S')}")

    async def auto_cleanup(self):
        """Фоновая задача для автоматического удаления"""
        while True:
            await asyncio.sleep(5)
            now = datetime.now()
            to_remove = []

            for file_path, delete_time in self.files_to_delete.items():
                if now >= delete_time:
                    if self.delete_file(file_path):
                        to_remove.append(file_path)

            for file_path in to_remove:
                del self.files_to_delete[file_path]

    def delete_file(self, file_path: str) -> bool:
        """Удалить один файл"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️ Удален файл: {file_path}")
                return True
        except Exception as e:
            print(f"❌ Ошибка удаления: {e}")
        return False

    def delete_all_temp_files(self) -> int:
        """Удалить все временные файлы"""
        deleted = 0
        for file in os.listdir(''):
            if file.startswith('temp_video_') or file.startswith('circle_'):
                if self.delete_file(file):
                    deleted += 1
        return deleted

    def delete_all_temp_files(self) -> int:
        """Удалить все временные файлы"""
        deleted = 0
        # Видео файлы
        for file in os.listdir(''):
            if (file.startswith('temp_video_') or file.startswith('circle_') or
                    file.startswith('temp_audio_') or file.startswith('voice_') or
                    file.startswith('temp_voice_') or file.startswith('audio_') or
            file.startswith('temp_gif_') or file.startswith('circle_gif_')):
                if self.delete_file(file):
                    deleted += 1
        return deleted

    def get_files_info(self) -> List[Dict]:
        """Получить информацию о временных файлах"""
        files_info = []
        for file in os.listdir(''):
            if file.startswith('temp_video_') or file.startswith('circle_'):
                stat = os.stat(file)
                files_info.append({
                    'name': file,
                    'size_mb': stat.st_size / (1024 * 1024),
                    'created': datetime.fromtimestamp(stat.st_ctime)
                })
        return files_info

def cleanup_all_temp():
    """Очистить все временные файлы"""
    deleted = cleaner.delete_all_temp_files()
    deleted += cleaner.cleanup_downloads_folder()
    return deleted

# Создаем глобальный экземпляр
cleaner = VideoCleaner()

async def start_cleaner_background():
    """Запустить фоновую очистку"""
    asyncio.create_task(cleaner.auto_cleanup())
    print("🧹 Менеджер очистки видео запущен")


def cleanup_all_temp() -> int:
    """Очистить все временные файлы"""
    deleted = cleaner.delete_all_temp_files()
    deleted += cleaner.cleanup_downloads_folder()
    return deleted


def schedule_delete_after_delay(file_path: str, seconds: int = 60):
    """Удалить файл через N секунд"""
    cleaner.schedule_deletion(file_path, seconds)

async def start_cleaner_background():
    """Запустить фоновую очистку"""
    asyncio.create_task(cleaner.auto_cleanup())
    print("🧹 Менеджер очистки видео запущен")


def cleanup_all_temp() -> int:
    """Очистить все временные файлы"""
    return cleaner.delete_all_temp_files()