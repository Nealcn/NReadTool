"""阅读偏好接口"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_device_id
from app.schemas.common import success, ApiResponse
from app.schemas.reading_setting import ReadingSettingUpsert
from app.services.reading_setting_service import ReadingSettingService

router = APIRouter(prefix="/reading", tags=["阅读偏好"])


@router.get("/settings", response_model=ApiResponse)
async def get_settings(device_id: str = Depends(get_device_id), db: Session = Depends(get_db)):
    settings = ReadingSettingService.get_all(db, device_id)
    return success(data=settings)


@router.put("/settings", response_model=ApiResponse)
async def upsert_setting(req: ReadingSettingUpsert, device_id: str = Depends(get_device_id), db: Session = Depends(get_db)):
    ReadingSettingService.upsert(db, device_id, req.key, req.value)
    return success(message="设置已保存")
