"""AI 划词 Schema"""

from typing import Optional, Literal

from pydantic import BaseModel, Field


class AIExplainRequest(BaseModel):
    """AI 解读请求"""
    text: str = Field(..., max_length=2000, description="用户选中文本（≤2000字）")
    type: Literal["word", "sentence", "grammar", "background"] = "word"
    book_id: Optional[int] = None
    chapter_title: Optional[str] = None


class AIExplainResponse(BaseModel):
    """AI 解读响应"""
    explanation: str
    type: str
    model: str = "deepseek-chat"


class AIHealthResponse(BaseModel):
    """AI 健康检查响应"""
    available: bool
