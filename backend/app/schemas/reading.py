"""阅读进度 Schema — FK 改为 file_hash"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReadingProgressRequest(BaseModel):
    spine_index: int
    content_id: int
    scroll_percent: float = 0.0


class ReadingProgressResponse(BaseModel):
    book_hash: str
    spine_index: int
    content_id: int
    scroll_percent: float
    updated_at: datetime

    class Config:
        from_attributes = True
