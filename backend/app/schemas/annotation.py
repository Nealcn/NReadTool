"""高亮/笔记 Schema"""

from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel


class AnnotationCreate(BaseModel):
    cfi: str
    type: Literal["highlight", "note", "bookmark"] = "highlight"
    style: Optional[str] = None
    color: Optional[str] = None
    text: Optional[str] = None
    note: Optional[str] = None


class AnnotationUpdate(BaseModel):
    style: Optional[str] = None
    color: Optional[str] = None
    note: Optional[str] = None


class AnnotationResponse(BaseModel):
    id: int
    book_hash: str
    device_id: str
    cfi: str
    type: str
    style: Optional[str] = None
    color: Optional[str] = None
    text: Optional[str] = None
    note: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
