import os
import asyncio
from typing import Optional, Tuple
import yt_dlp


class VideoDownloader:
    def __init__(self):
        self.download_path = "downloads"
        os.makedirs(self.download_path, exist_ok=True)

    def detect_platform(self, url: str) -> Optional[str]:
        """Определяет платформу по ссылке"""
        url_lower = url.lower()

        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'youtube'
        elif 'tiktok.com' in url_lower or 'vm.tiktok' in url_lower:
            return 'tiktok'
        elif 'instagram.com' in url_lower or 'instagr.am' in url_lower:
            return 'instagram'
        return None

    async def download_video(self, url: str, platform: str) -> Tuple[Optional[str], Optional[str]]:
        if platform == 'youtube':
            return await self._download_youtube(url)
        elif platform == 'tiktok':
            return await self._download_tiktok(url)
        elif platform == 'instagram':
            return await self._download_instagram(url)
        return None, None

    # =========================================================
    # YOUTUBE (НЕ ИЗМЕНИЛОСЬ)
    # =========================================================
    async def _download_youtube(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            ydl_opts = {
                'format': 'best[height<=1080]',  # Максимальное качество до 1080p (быстрее)
                # 'format': 'best',  # Раскомментируй для 4K
                'outtmpl': os.path.join(self.download_path, '%(title)s_%(id)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            }

            loop = asyncio.get_event_loop()

            def download():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    return ydl.prepare_filename(info).replace('.webm', '.mp4').replace('.mkv', '.mp4')

            filepath = await loop.run_in_executor(None, download)

            if filepath and os.path.exists(filepath):
                return filepath, "YouTube"
            return None, None

        except Exception as e:
            print(f"YouTube download error: {e}")
            return None, None

    # =========================================================
    # TIKTOK (ТВОЙ ПРОКСИ СОХРАНЁН! НИЧЕГО НЕ УДАЛЕНО)
    # =========================================================
    async def _download_tiktok(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            # ===== ТВОИ НАСТРОЙКИ ПРОКСИ (СОХРАНЕНЫ) =====
            # Если у тебя был прокси, он здесь. Ничего не удалял!

            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(self.download_path, 'tiktok_%(id)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                # 👇 ТВОЙ ПРОКСИ (ЕСЛИ БЫЛ, ОН ОСТАЛСЯ)
                'proxy' : 'socks5://8NXVo5:MsxRMQ@185.79.132.129:8000',
                # 'proxy': 'socks5://твой_прокси:порт',  ← Раскомментируй если нужен
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                }
            }

            loop = asyncio.get_event_loop()

            def download():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    return ydl.prepare_filename(info)

            filepath = await loop.run_in_executor(None, download)

            if filepath and os.path.exists(filepath):
                return filepath, "TikTok"
            return None, None

        except Exception as e:
            print(f"TikTok download error: {e}")
            return None, None

    # =========================================================
    # INSTAGRAM (НЕ ИЗМЕНИЛОСЬ)
    # =========================================================
    async def _download_instagram(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(self.download_path, 'instagram_%(id)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                }
            }

            loop = asyncio.get_event_loop()

            def download():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    return ydl.prepare_filename(info)

            filepath = await loop.run_in_executor(None, download)

            if os.path.exists(filepath):
                return filepath, "Instagram"
            return None, None

        except Exception as e:
            print(f"Instagram download error: {e}")
            return None, None


downloader = VideoDownloader()