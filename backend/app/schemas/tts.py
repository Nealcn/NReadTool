"""TTS 语音合成 Schema"""

from pydantic import BaseModel, Field


class TTSSpeakRequest(BaseModel):
    """TTS 合成请求"""
    input: str = Field(..., min_length=1, max_length=5000, description="要合成的文本")
    voice: str = Field(..., description="语音 ID，如 zh-CN-XiaoxiaoNeural")
    lang: str = Field(..., description="语言代码，如 zh-CN")
    pitch: float = Field(default=1.0, ge=0.5, le=1.5, description="音调 (0.5-1.5)")
    rate: float = Field(default=1.0, ge=0.5, le=2.0, description="语速 (0.5-2.0)")


class TTSVoiceItem(BaseModel):
    """TTS 语音项"""
    name: str
    id: str
    lang: str


class TTSVoicesResponse(BaseModel):
    """TTS 语音列表响应"""
    voices: list[TTSVoiceItem]
