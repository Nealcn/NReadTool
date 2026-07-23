"""阅读偏好模型"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint

from app.core.database import Base


class ReadingSetting(Base):
    __tablename__ = "reading_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(64), nullable=False)
    key = Column(String(128), nullable=False)
    value = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("device_id", "key", name="uq_device_setting_key"),
    )
