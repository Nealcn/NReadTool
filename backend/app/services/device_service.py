"""设备管理服务"""

from sqlalchemy.orm import Session

from app.models.device import Device
from app.schemas.device import DeviceRegisterRequest, DeviceInfo


class DeviceService:
    """设备管理"""

    @staticmethod
    def register(db: Session, req: DeviceRegisterRequest) -> DeviceInfo:
        """注册或更新设备信息"""
        device = db.query(Device).filter(Device.device_id == req.device_id).first()
        if device:
            # 更新信息
            if req.device_name:
                device.device_name = req.device_name
            if req.platform:
                device.platform = req.platform
        else:
            device = Device(
                device_id=req.device_id,
                device_name=req.device_name,
                platform=req.platform,
            )
            db.add(device)

        db.commit()
        db.refresh(device)
        return DeviceInfo.model_validate(device)

    @staticmethod
    def get_by_device_id(db: Session, device_id: str) -> Device | None:
        """根据设备 ID 获取设备信息"""
        return db.query(Device).filter(Device.device_id == device_id).first()
