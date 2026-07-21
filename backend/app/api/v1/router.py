"""v1 路由聚合"""

from fastapi import APIRouter

from app.api.v1.books import router as books_router
from app.api.v1.reading import router as reading_router
from app.api.v1.ai import router as ai_router
from app.api.v1.ai_chat import router as ai_chat_router
from app.api.v1.devices import router as devices_router
from app.api.v1.tts import router as tts_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(books_router)
api_router.include_router(reading_router)
api_router.include_router(ai_router)
api_router.include_router(ai_chat_router)
api_router.include_router(devices_router)
api_router.include_router(tts_router)
