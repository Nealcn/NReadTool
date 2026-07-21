"""AI 多轮对话接口"""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.schemas.common import success, ApiResponse
from app.services.ai_chat_service import AIChatService
from app.core.exceptions import AIServiceUnavailableException

router = APIRouter(prefix="/ai", tags=["AI 对话"])


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    """聊天请求"""
    messages: list[ChatMessage] = Field(..., min_length=1, max_length=50)
    book_id: int | None = None
    chapter_title: str | None = None


class ChatResponse(BaseModel):
    """聊天响应"""
    reply: str


@router.post("/chat", response_model=ApiResponse)
async def ai_chat(req: ChatRequest):
    """AI 多轮对话"""
    try:
        service = AIChatService()
        reply = service.chat(
            messages=[m.model_dump() for m in req.messages],
            book_id=req.book_id,
            chapter_title=req.chapter_title,
        )
        return success(data=ChatResponse(reply=reply).model_dump())
    except AIServiceUnavailableException:
        raise
    except Exception as e:
        raise AIServiceUnavailableException(f"AI 对话服务调用失败: {str(e)}")
