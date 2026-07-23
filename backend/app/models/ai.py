"""AI 对话模型"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey

from app.core.database import Base


class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id = Column(String(64), primary_key=True)  # 前端生成的 UUID
    book_hash = Column(String(64), ForeignKey("books.file_hash", ondelete="CASCADE"), nullable=False, index=True)
    device_id = Column(String(64), nullable=False)
    title = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AIMessage(Base):
    __tablename__ = "ai_messages"

    id = Column(String(64), primary_key=True)  # 前端生成的 UUID
    conversation_id = Column(String(64), ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(16), nullable=False)  # user / assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
