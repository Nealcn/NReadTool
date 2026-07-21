"""阅读进度 Schema"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReadingProgressRequest(BaseModel):
    """保存阅读进度请求"""
    spine_index: int
    content_id: int
    scroll_percent: float = 0.0


class ReadingProgressResponse(BaseModel):
    """阅读进度响应"""
    book_id: int
    spine_index: int
    content_id: int
    scroll_percent: float
    updated_at: datetime

    class Config:
        from_attributes = True
