"""阅读偏好服务"""

from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.reading_setting import ReadingSetting


class ReadingSettingService:

    @staticmethod
    def get_all(db: Session, device_id: str) -> Dict[str, str]:
        settings = db.query(ReadingSetting).filter(
            ReadingSetting.device_id == device_id,
        ).all()
        return {s.key: s.value for s in settings}

    @staticmethod
    def upsert(db: Session, device_id: str, key: str, value: str) -> None:
        stmt = text("""
            INSERT INTO reading_settings (device_id, key, value, updated_at)
            VALUES (:device_id, :key, :value, CURRENT_TIMESTAMP)
            ON CONFLICT(device_id, key) DO UPDATE SET
                value = :value,
                updated_at = CURRENT_TIMESTAMP
        """)
        db.execute(stmt, {"device_id": device_id, "key": key, "value": value})
        db.commit()
