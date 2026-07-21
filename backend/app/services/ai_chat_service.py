"""AI 聊天服务 - 多轮对话"""

from openai import OpenAI

from app.config import settings
from app.core.exceptions import AIServiceUnavailableException

# 系统提示词：阅读助手
SYSTEM_PROMPT = """你是一个专业的阅读助手，擅长帮助读者理解书籍内容。
你可以根据用户选中的文本和对话历史，提供准确的解释、分析和回答。
回答应简洁清晰，使用中文，适当使用 Markdown 格式增强可读性。

当前的对话上下文：
- 用户选中了一段文本让你解读
- 你可以参考对话历史来理解用户的问题
- 首条消息通常是对选中文本的解释
- 后续问题可能是在之前讨论基础上的追问"""


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

    def chat(self, messages: list[dict], book_id: int = None, chapter_title: str = None) -> str:
        """多轮对话

        messages: [
            {"role": "user", "content": "解释这句话：..."},
            {"role": "assistant", "content": "..."},
            {"role": "user", "content": "接着说"},
        ]
        """
        system = SYSTEM_PROMPT
        context_parts = []
        if book_id:
            context_parts.append(f"书籍 ID: {book_id}")
        if chapter_title:
            context_parts.append(f"当前章节: {chapter_title}")
        if context_parts:
            system += "\n\n当前阅读上下文：\n" + "\n".join(context_parts)

        try:
            response = self.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    *messages,
                ],
                max_tokens=settings.AI_MAX_TOKENS,
                temperature=0.3,
            )
        except Exception as e:
            error_str = str(e).lower()
            if "timeout" in error_str:
                raise AIServiceUnavailableException("AI 服务繁忙，请稍后重试")
            raise AIServiceUnavailableException(f"AI 服务调用失败: {str(e)}")

        content = response.choices[0].message.content
        if not content:
            content = "暂无法回答该问题，请重新尝试。"

        return content
