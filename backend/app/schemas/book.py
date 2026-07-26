"""书籍相关 Schema — 主键改为 file_hash"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class BookInfo(BaseModel):
    file_hash: str
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
    file_hash: str
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
    title: str


class BookMetadataUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    language: Optional[str] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None  # base64 encoded image


class TOCItem(BaseModel):
    spine_index: int
    content_id: int
    title: str


class TOCResponse(BaseModel):
    book_hash: str
    items: List[TOCItem]


class ChapterContent(BaseModel):
    spine_index: int
    title: Optional[str] = None
    html_content: str


class BookListResponse(BaseModel):
    books: List[BookInfo]
    total: int
