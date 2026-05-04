import os
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict


class VideoCleaner:
    def __init__(self):
        self.files_to_delete = {}
        self.downloads_path = "downloads"
        os.makedirs(self.downloads_path, exist_ok=True)

    def schedule_deletion(self, file_path: str, seconds_delay: int = 60):
        delete_time = datetime.now() + timedelta(seconds=seconds_delay)
        self.files_to_delete[file_path] = delete_time
        print(f"📅 Файл {os.path.basename(file_path)} будет удален в {delete_time.strftime('%H:%M:%S')}")

    async def auto_cleanup(self):
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
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️ Удален файл: {os.path.basename(file_path)}")
                return True
        except Exception as e:
            print(f"❌ Ошибка удаления {file_path}: {e}")
        return False

    def delete_all_temp_files(self) -> int:
        deleted = 0
        prefixes = ('temp_video_', 'circle_', 'temp_audio_', 'voice_', 'temp_voice_', 'audio_', 'temp_gif_', 'circle_gif_')
        for file in os.listdir('.'):
            if file.startswith(prefixes):
                if self.delete_file(file):
                    deleted += 1
        return deleted

    def cleanup_downloads_folder(self) -> int:
        if not os.path.exists(self.downloads_path):
            return 0
        deleted = 0
        for file in os.listdir(self.downloads_path):
            filepath = os.path.join(self.downloads_path, file)
            if self.delete_file(filepath):
                deleted += 1
        return deleted

    def get_files_info(self) -> List[Dict]:
        files_info = []
        # Файлы в текущей директории
        for file in os.listdir('.'):
            if file.startswith(('temp_video_', 'circle_', 'temp_audio_', 'voice_', 'temp_voice_', 'audio_', 'temp_gif_', 'circle_gif_')):
                try:
                    stat = os.stat(file)
                    files_info.append({
                        'name': file,
                        'size_mb': stat.st_size / (1024 * 1024),
                        'created': datetime.fromtimestamp(stat.st_ctime),
                        'path': file
                    })
                except:
                    pass
        # Файлы в папке downloads
        if os.path.exists(self.downloads_path):
            for file in os.listdir(self.downloads_path):
                filepath = os.path.join(self.downloads_path, file)
                try:
                    stat = os.stat(filepath)
                    files_info.append({
                        'name': f"downloads/{file}",
                        'size_mb': stat.st_size / (1024 * 1024),
                        'created': datetime.fromtimestamp(stat.st_ctime),
                        'path': filepath
                    })
                except:
                    pass
        return files_info


# Глобальный экземпляр
cleaner = VideoCleaner()


async def start_cleaner_background():
    asyncio.create_task(cleaner.auto_cleanup())
    print("🧹 Менеджер очистки видео запущен")


def cleanup_all_temp() -> int:
    return cleaner.delete_all_temp_files() + cleaner.cleanup_downloads_folder()


def schedule_delete_after_delay(file_path: str, seconds: int = 60):
    cleaner.schedule_deletion(file_path, seconds)