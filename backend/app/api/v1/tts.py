"""TTS 语音合成接口"""

import json
from urllib.parse import quote

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.schemas.common import success
from app.schemas.tts import TTSSpeakRequest, TTSVoicesResponse, TTSVoiceItem
from app.services.tts_service import TTSService

router = APIRouter(prefix="/tts", tags=["TTS 语音"])


@router.post("/speak")
async def tts_speak(req: TTSSpeakRequest):
    """合成语音并返回 MP3 音频"""
    try:
        audio_bytes, boundaries = await TTSService.speak(req)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"TTS 合成失败: {str(e)}",
        )

    if not audio_bytes:
        raise HTTPException(status_code=502, detail="TTS 合成未生成音频数据")

    # Word boundaries: URL-encoded JSON in response header
    # 匹配前端 EdgeTTS 已有的 WORD_BOUNDARIES_HEADER 解析逻辑
    boundaries_json = json.dumps(boundaries, ensure_ascii=False)
    encoded_boundaries = quote(boundaries_json)

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={
            "X-TTS-Word-Boundaries": encoded_boundaries,
            "Content-Length": str(len(audio_bytes)),
            "Cache-Control": "no-cache",
        },
    )


@router.get("/voices")
async def tts_voices():
    """获取所有可用 TTS 语音列表"""
    try:
        voices_data = await TTSService.get_voices()
        voices = [TTSVoiceItem(**v) for v in voices_data]
        return success(data=TTSVoicesResponse(voices=voices).model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"获取语音列表失败: {str(e)}",
        )
