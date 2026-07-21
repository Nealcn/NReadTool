"""设备 Schema"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DeviceRegisterRequest(BaseModel):
    """设备注册请求"""
    device_id: str
    device_name: Optional[str] = None
    platform: Optional[str] = "web"


class DeviceInfo(BaseModel):
    """设备信息"""
    device_id: str
    device_name: Optional[str] = None
    platform: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
