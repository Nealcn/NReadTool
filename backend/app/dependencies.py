"""FastAPI 依赖注入"""

from fastapi import Header, HTTPException
from typing import Optional


async def get_device_id(
    x_device_id: Optional[str] = Header(None, alias="X-Device-Id"),
) -> str:
    """从请求头获取设备 ID"""
    if not x_device_id:
        raise HTTPException(status_code=400, detail="Missing X-Device-Id header")
    return x_device_id
