"""书籍结构化内容模型"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey

from app.core.database import Base


class BookContent(Base):
    """章节内容"""
    __tablename__ = "book_contents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    spine_index = Column(Integer, nullable=False)  # 阅读顺序（0-based）
    chapter_title = Column(String(512), nullable=True)
    href = Column(String(512), nullable=True)
    html_content = Column(Text, nullable=False)  # 含标签的原始 HTML
    plain_text = Column(Text, nullable=True)  # 纯文本（AI 截断用）
    word_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class BookSpine(Base):
    """Spine 阅读顺序"""
    __tablename__ = "book_spine"

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    spine_index = Column(Integer, nullable=False)
    content_id = Column(Integer, ForeignKey("book_contents.id", ondelete="CASCADE"), nullable=False)
    is_linear = Column(Integer, default=1)  # Boolean: 是否在标准阅读流中
    created_at = Column(DateTime, default=datetime.utcnow)
