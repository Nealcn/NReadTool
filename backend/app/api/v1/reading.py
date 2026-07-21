"""阅读进度接口"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_device_id
from app.schemas.common import success, ApiResponse
from app.schemas.reading import ReadingProgressRequest, ReadingProgressResponse
from app.services.reading_service import ReadingService

router = APIRouter(prefix="/reading", tags=["阅读进度"])


@router.get("/progress/{book_id}", response_model=ApiResponse)
async def get_progress(
    book_id: int,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    """获取阅读进度"""
    progress = ReadingService.get_progress(db, device_id, book_id)
    if progress is None:
        return success(data=None, message="暂无阅读进度")
    return success(data=progress.model_dump())


@router.put("/progress/{book_id}", response_model=ApiResponse)
async def save_progress(
    book_id: int,
    req: ReadingProgressRequest,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    """保存阅读进度"""
    progress = ReadingService.save_progress(db, device_id, book_id, req)
    return success(data=progress.model_dump(), message="进度已保存")


@router.delete("/progress/{book_id}", response_model=ApiResponse)
async def clear_progress(
    book_id: int,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    """清除阅读进度"""
    ReadingService.clear_progress(db, device_id, book_id)
    return success(message="进度已清除")
