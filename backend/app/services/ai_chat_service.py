"""AI 聊天服务 - 多轮对话 + 对话 CRUD"""

from typing import List
from openai import OpenAI
from sqlalchemy.orm import Session

from app.config import settings
from app.core.exceptions import AIServiceUnavailableException
from app.models.ai import AIConversation, AIMessage
from app.schemas.ai import AIConversationCreate, AIConversationResponse, AIMessageCreate, AIMessageResponse

SYSTEM_PROMPT = """你是一个专业的阅读助手，擅长帮助读者理解书籍内容。
你可以根据用户选中的文本和对话历史，提供准确的解释、分析和回答。
回答应简洁清晰，使用中文，适当使用 Markdown 格式增强可读性。"""


class AIChatService:
    """AI 多轮对话服务"""

    def __init__(self):
        if not settings.DEEPSEEK_API_KEY:
            raise AIServiceUnavailableException("DeepSeek API Key 未配置")
        self.client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
            timeout=settings.AI_REQUEST_TIMEOUT,
        )

    def chat(self, messages: list[dict], book_hash: str = None, chapter_title: str = None) -> str:
        """多轮对话"""
        system = SYSTEM_PROMPT
        context_parts = []
        if book_hash:
            context_parts.append(f"书籍: {book_hash}")
        if chapter_title:
            context_parts.append(f"当前章节: {chapter_title}")
        if context_parts:
            system += "\n\n当前阅读上下文：\n" + "\n".join(context_parts)

        try:
            response = self.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[{"role": "system", "content": system}, *messages],
                max_tokens=settings.AI_MAX_TOKENS,
                temperature=0.3,
            )
        except Exception as e:
            error_str = str(e).lower()
            if "timeout" in error_str:
                raise AIServiceUnavailableException("AI 服务繁忙，请稍后重试")
            raise AIServiceUnavailableException(f"AI 服务调用失败: {str(e)}")

        content = response.choices[0].message.content
        return content or "暂无法回答该问题，请重新尝试。"

    # ---- 对话 CRUD ----

    def create_conversation(self, db: Session, book_hash: str, device_id: str, req: AIConversationCreate) -> AIConversationResponse:
        conv = AIConversation(id=req.id, book_hash=book_hash, device_id=device_id, title=req.title)
        db.add(conv)
        db.commit()
        db.refresh(conv)
        return AIConversationResponse.model_validate(conv)

    def list_conversations(self, db: Session, book_hash: str, device_id: str) -> List[AIConversationResponse]:
        convs = db.query(AIConversation).filter(
            AIConversation.book_hash == book_hash,
            AIConversation.device_id == device_id,
        ).order_by(AIConversation.updated_at.desc()).all()
        return [AIConversationResponse.model_validate(c) for c in convs]

    def add_message(self, db: Session, conversation_id: str, req: AIMessageCreate) -> AIMessageResponse:
        msg = AIMessage(id=req.id, conversation_id=conversation_id, role=req.role, content=req.content)
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return AIMessageResponse.model_validate(msg)

    def get_messages(self, db: Session, conversation_id: str) -> List[AIMessageResponse]:
        msgs = db.query(AIMessage).filter(AIMessage.conversation_id == conversation_id).order_by(AIMessage.created_at).all()
        return [AIMessageResponse.model_validate(m) for m in msgs]
