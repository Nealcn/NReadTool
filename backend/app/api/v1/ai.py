"""AI 划词接口"""

from fastapi import APIRouter

from app.schemas.common import success, ApiResponse
from app.schemas.ai import AIExplainRequest, AIExplainResponse, AIHealthResponse
from app.services.ai_service import AIService
from app.core.exceptions import AIServiceUnavailableException

router = APIRouter(prefix="/ai", tags=["AI 划词"])


@router.post("/explain", response_model=ApiResponse)
async def ai_explain(req: AIExplainRequest):
    try:
        service = AIService()
        result = service.explain(req)
        return success(data=result.model_dump())
    except AIServiceUnavailableException:
        raise
    except Exception as e:
        raise AIServiceUnavailableException(f"AI 服务调用失败: {str(e)}")


@router.get("/health", response_model=ApiResponse)
async def ai_health():
    available = AIService.health()
    return success(data=AIHealthResponse(available=available).model_dump())
