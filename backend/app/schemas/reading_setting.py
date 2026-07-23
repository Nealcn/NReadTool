"""阅读偏好 Schema"""

from pydantic import BaseModel


class ReadingSettingUpsert(BaseModel):
    key: str
    value: str
