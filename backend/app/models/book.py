"""书籍元信息模型 — 主键改为 file_hash"""

from datetime import datetime

from sqlalchemy import Column, String, Integer, Text, DateTime

from app.core.database import Base


class Book(Base):
    __tablename__ = "books"

    file_hash = Column(String(64), primary_key=True)  # SHA256, 与 Readest 对齐
    title = Column(String(512), nullable=False)
    author = Column(String(256), nullable=True)
    cover_image = Column(Text, nullable=True)
    publisher = Column(String(256), nullable=True)
    language = Column(String(32), nullable=True)
    isbn = Column(String(64), nullable=True)
    description = Column(Text, nullable=True)
    file_name = Column(String(256), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(Text, nullable=False)
    total_chapters = Column(Integer, default=0)
    total_words = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
