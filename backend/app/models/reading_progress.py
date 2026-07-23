"""阅读进度模型 — FK 改为 file_hash"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint

from app.core.database import Base


class ReadingProgress(Base):
    __tablename__ = "reading_progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(64), nullable=False)
    book_hash = Column(String(64), ForeignKey("books.file_hash", ondelete="CASCADE"), nullable=False)
    spine_index = Column(Integer, nullable=False, default=0)
    content_id = Column(Integer, ForeignKey("book_contents.id"), nullable=False)
    scroll_percent = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("device_id", "book_hash", name="uq_device_book_progress"),
    )
