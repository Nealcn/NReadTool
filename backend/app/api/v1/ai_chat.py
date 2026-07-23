"""AI 对话接口 — 简单对话 + 对话 CRUD"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_device_id
from app.schemas.common import success, ApiResponse
from app.schemas.ai import AIConversationCreate, AIMessageCreate
from app.services.ai_chat_service import AIChatService
from app.core.exceptions import AIServiceUnavailableException

router = APIRouter(prefix="/ai", tags=["AI 对话"])


# ---- 简单对话 (原有的 /chat 端点) ----

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., min_length=1, max_length=50)
    book_hash: str | None = None
    chapter_title: str | None = None


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ApiResponse)
async def ai_chat(req: ChatRequest):
    """AI 多轮对话"""
    try:
        service = AIChatService()
        reply = service.chat(
            messages=[m.model_dump() for m in req.messages],
            book_hash=req.book_hash,
            chapter_title=req.chapter_title,
        )
        return success(data=ChatResponse(reply=reply).model_dump())
    except AIServiceUnavailableException:
        raise
    except Exception as e:
        raise AIServiceUnavailableException(f"AI 对话服务调用失败: {str(e)}")


# ---- 对话 CRUD ----

@router.post("/conversations/{book_hash}", response_model=ApiResponse)
async def create_conversation(
    book_hash: str, req: AIConversationCreate,
    device_id: str = Depends(get_device_id), db: Session = Depends(get_db),
):
    svc = AIChatService()
    conv = svc.create_conversation(db, book_hash, device_id, req)
    return success(data=conv.model_dump())


@router.get("/conversations/{book_hash}", response_model=ApiResponse)
async def list_conversations(
    book_hash: str,
    device_id: str = Depends(get_device_id), db: Session = Depends(get_db),
):
    svc = AIChatService()
    convs = svc.list_conversations(db, book_hash, device_id)
    return success(data=[c.model_dump() for c in convs])


@router.post("/messages/{conv_id}", response_model=ApiResponse)
async def add_message(conv_id: str, req: AIMessageCreate, db: Session = Depends(get_db)):
    svc = AIChatService()
    msg = svc.add_message(db, conv_id, req)
    return success(data=msg.model_dump())


@router.get("/messages/{conv_id}", response_model=ApiResponse)
async def get_messages(conv_id: str, db: Session = Depends(get_db)):
    svc = AIChatService()
    msgs = svc.get_messages(db, conv_id)
    return success(data=[m.model_dump() for m in msgs])
