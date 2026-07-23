"""书籍结构化内容模型 — FK 改为 file_hash"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey

from app.core.database import Base


class BookContent(Base):
    __tablename__ = "book_contents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_hash = Column(String(64), ForeignKey("books.file_hash", ondelete="CASCADE"), nullable=False, index=True)
    spine_index = Column(Integer, nullable=False)
    chapter_title = Column(String(512), nullable=True)
    href = Column(String(512), nullable=True)
    html_content = Column(Text, nullable=False)
    plain_text = Column(Text, nullable=True)
    word_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class BookSpine(Base):
    __tablename__ = "book_spine"

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_hash = Column(String(64), ForeignKey("books.file_hash", ondelete="CASCADE"), nullable=False, index=True)
    spine_index = Column(Integer, nullable=False)
    content_id = Column(Integer, ForeignKey("book_contents.id", ondelete="CASCADE"), nullable=False)
    is_linear = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
