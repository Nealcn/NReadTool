"""高亮/笔记/批注模型"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey

from app.core.database import Base


class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_hash = Column(String(64), ForeignKey("books.file_hash", ondelete="CASCADE"), nullable=False, index=True)
    device_id = Column(String(64), nullable=False)
    cfi = Column(String(256), nullable=False)  # EPUB CFI 定位符
    type = Column(String(32), nullable=False, default="highlight")  # highlight / note / bookmark
    style = Column(String(32), nullable=True)  # 高亮样式
    color = Column(String(32), nullable=True)  # 高亮颜色
    text = Column(Text, nullable=True)  # 选中的文本
    note = Column(Text, nullable=True)  # 用户笔记
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
