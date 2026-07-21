"""书籍相关 Schema"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class BookInfo(BaseModel):
    """书籍信息"""
    id: int
    title: str
    author: Optional[str] = None
    cover_image: Optional[str] = None
    file_size: int
    total_chapters: int
    total_words: int
    created_at: datetime

    class Config:
        from_attributes = True


class BookDetail(BaseModel):
    """书籍详情"""
    id: int
    title: str
    author: Optional[str] = None
    cover_image: Optional[str] = None
    publisher: Optional[str] = None
    language: Optional[str] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    file_name: str
    file_size: int
    total_chapters: int
    total_words: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookRenameRequest(BaseModel):
    """重命名请求"""
    title: str


class TOCItem(BaseModel):
    """章节目录项"""
    spine_index: int
    content_id: int
    title: str


class TOCResponse(BaseModel):
    """章节目录"""
    book_id: int
    items: List[TOCItem]


class ChapterContent(BaseModel):
    """章节内容"""
    spine_index: int
    title: Optional[str] = None
    html_content: str


class BookListResponse(BaseModel):
    """书籍列表"""
    books: List[BookInfo]
    total: int
