"""AI 对话 Schema"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class AIConversationCreate(BaseModel):
    id: str  # 前端生成的 UUID
    title: Optional[str] = None


class AIConversationResponse(BaseModel):
    id: str
    book_hash: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AIMessageCreate(BaseModel):
    id: str  # 前端生成的 UUID
    role: str  # user / assistant
    content: str


class AIMessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class AIExplainRequest(BaseModel):
    text: str
    type: str = "sentence"


class AIExplainResponse(BaseModel):
    explanation: str
    type: str
    model: str = "deepseek-chat"


class AIHealthResponse(BaseModel):
    available: bool
