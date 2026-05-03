from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    user_id: int
    username: Optional[str]
    first_name: str
    last_name: Optional[str]
    language: str
    is_banned: bool
    is_admin: bool
    created_at: datetime
    last_active: datetime

@dataclass
class VideoFile:
    file_id: int
    user_id: int
    original_file_id: str
    converted_file_path: str
    file_size: int
    created_at: datetime
    deleted_at: Optional[datetime]