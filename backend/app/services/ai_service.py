"""AI 划词服务 - DeepSeek API 调用"""

from openai import OpenAI

from app.config import settings
from app.schemas.ai import AIExplainRequest, AIExplainResponse
from app.core.exceptions import AIRequestTimeoutException, AIServiceUnavailableException


# Prompt 模板
SYSTEM_PROMPT = """你是一个专业的阅读助手，擅长帮助读者理解书籍内容。
请根据用户选中的文本内容和标注的类型，提供准确、易懂的解释。
回答应简洁清晰，使用中文，适当使用 Markdown 格式增强可读性。
注意：你只针对用户提供的片段进行解释，不要假设未提供的上下文信息。"""

TYPE_PROMPTS = {
    "word": '用户选中了以下文本中的词语/字："{text}"。请解释该词的含义、词性、用法，如有多个含义请列出最相关的。',
    "sentence": '用户选中了以下句子："{text}"。请解析这句话的含义、修辞手法（如有）、在上下文中的作用。',
    "grammar": '用户选中了以下文本："{text}"。请对其中的语法结构、句式特点进行解读，如涉及外语请说明语法规则。',
    "background": '用户选中了以下文本："{text}"。请扩展介绍相关的历史背景、文化背景、作者意图或相关知识。',
}


class AIService:
    """AI 划词服务"""

    def __init__(self):
        if not settings.DEEPSEEK_API_KEY:
            raise AIServiceUnavailableException("DeepSeek API Key 未配置")

        self.client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
            timeout=settings.AI_REQUEST_TIMEOUT,
        )

    def explain(self, request: AIExplainRequest) -> AIExplainResponse:
        """调用 DeepSeek 进行文本解读"""
        # 截断校验
        text = request.text[:2000]

        # 构造 Prompt
        prompt_template = TYPE_PROMPTS.get(request.type, TYPE_PROMPTS["sentence"])
        user_prompt = prompt_template.format(text=text)

        try:
            response = self.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=settings.AI_MAX_TOKENS,
                temperature=0.3,
            )
        except Exception as e:
            error_str = str(e).lower()
            if "timeout" in error_str:
                raise AIRequestTimeoutException()
            raise AIServiceUnavailableException(f"AI 服务调用失败: {str(e)}")

        content = response.choices[0].message.content
        if not content:
            content = "暂无法解读该内容，请重新尝试。"

        return AIExplainResponse(
            explanation=content,
            type=request.type,
            model=settings.AI_MODEL,
        )

    @staticmethod
    def health() -> bool:
        """健康检查 - 仅检查 API Key 是否配置"""
        return bool(settings.DEEPSEEK_API_KEY)
