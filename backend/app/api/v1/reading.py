"""阅读进度接口 — FK 改为 file_hash"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_device_id
from app.schemas.common import success, ApiResponse
from app.schemas.reading import ReadingProgressRequest
from app.services.reading_service import ReadingService

router = APIRouter(prefix="/reading", tags=["阅读进度"])


@router.get("/progress/{book_hash}", response_model=ApiResponse)
async def get_progress(book_hash: str, device_id: str = Depends(get_device_id), db: Session = Depends(get_db)):
    progress = ReadingService.get_progress(db, device_id, book_hash)
    if progress is None:
        return success(data=None, message="暂无阅读进度")
    return success(data=progress.model_dump())


@router.put("/progress/{book_hash}", response_model=ApiResponse)
async def save_progress(book_hash: str, req: ReadingProgressRequest, device_id: str = Depends(get_device_id), db: Session = Depends(get_db)):
    progress = ReadingService.save_progress(db, device_id, book_hash, req)
    return success(data=progress.model_dump(), message="进度已保存")


@router.delete("/progress/{book_hash}", response_model=ApiResponse)
async def clear_progress(book_hash: str, device_id: str = Depends(get_device_id), db: Session = Depends(get_db)):
    ReadingService.clear_progress(db, device_id, book_hash)
    return success(message="进度已清除")
