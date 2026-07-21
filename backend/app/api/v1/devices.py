"""设备注册接口"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import success, ApiResponse
from app.schemas.device import DeviceRegisterRequest, DeviceInfo
from app.services.device_service import DeviceService

router = APIRouter(prefix="/devices", tags=["设备管理"])


@router.post("/register", response_model=ApiResponse)
async def register_device(req: DeviceRegisterRequest, db: Session = Depends(get_db)):
    """注册或更新设备信息"""
    device = DeviceService.register(db, req)
    return success(data=DeviceInfo.model_validate(device).model_dump())
