"""书籍元信息模型"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime

from app.core.database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(512), nullable=False)
    author = Column(String(256), nullable=True)
    cover_image = Column(Text, nullable=True)  # Base64 编码
    publisher = Column(String(256), nullable=True)
    language = Column(String(32), nullable=True)
    isbn = Column(String(64), nullable=True)
    description = Column(Text, nullable=True)
    file_name = Column(String(256), nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)  # SHA256
    file_size = Column(Integer, nullable=False)
    file_path = Column(Text, nullable=False)
    total_chapters = Column(Integer, default=0)
    total_words = Column(Integer, default=0)
    upload_device_id = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)  # 软删除
