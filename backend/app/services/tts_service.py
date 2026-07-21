"""TTS 语音合成服务 - edge-tts 封装

优化策略：
1. 共享 aiohttp TCPConnector（复用 WebSocket 连接池，避免重复 SSL 握手）
2. 磁盘 + 内存两级 LRU 缓存（按文本 hash + 语音去重，跨进程持久化）
"""

import hashlib
import json
import os
import time
from collections import OrderedDict
from pathlib import Path
from typing import Optional

import aiohttp
from edge_tts import Communicate, list_voices

from app.schemas.tts import TTSSpeakRequest

# 磁盘缓存目录
CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "tts_cache"
CACHE_MAX_AGE = 3600 * 24 * 7  # 缓存保留 7 天
CACHE_MAX_FILES = 500  # 最多缓存 500 个文件

# 内存 LRU 缓存加速热数据
_MEM_CACHE: OrderedDict[str, tuple[bytes, list[dict]]] = OrderedDict()
_MEM_CACHE_MAX = 100

# 全局共享 TCPConnector
_connector: Optional[aiohttp.TCPConnector] = None


def _get_connector() -> aiohttp.TCPConnector:
    global _connector
    if _connector is None or _connector.closed:
        _connector = aiohttp.TCPConnector(
            limit=4,
            limit_per_host=2,
            force_close=False,
            ttl_dns_cache=300,
        )
    return _connector


def _cache_key(text: str, voice: str, pitch: float, rate: float) -> str:
    return hashlib.md5(
        f"{text}|{voice}|{pitch}|{rate}".encode()
    ).hexdigest()


def _cache_path(key: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{key}.mp3"


def _meta_path(key: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{key}.json"


def _load_from_disk(key: str) -> Optional[tuple[bytes, list[dict]]]:
    """从磁盘加载缓存的音频 + 边界"""
    mp3_path = _cache_path(key)
    meta_path = _meta_path(key)
    if not mp3_path.exists() or not meta_path.exists():
        return None
    # 检查过期
    age = time.time() - mp3_path.stat().st_mtime
    if age > CACHE_MAX_AGE:
        mp3_path.unlink(missing_ok=True)
        meta_path.unlink(missing_ok=True)
        return None
    try:
        audio = mp3_path.read_bytes()
        boundaries = json.loads(meta_path.read_text())
        return audio, boundaries
    except (OSError, json.JSONDecodeError):
        return None


def _save_to_disk(key: str, audio: bytes, boundaries: list[dict]):
    """保存音频 + 边界到磁盘缓存"""
    try:
        # 清理旧缓存
        _evict_if_needed()
        _cache_path(key).write_bytes(audio)
        _meta_path(key).write_text(json.dumps(boundaries, ensure_ascii=False))
    except OSError:
        pass  # 缓存写入失败不影响核心功能


def _evict_if_needed():
    """缓存文件数超限时清理最旧的"""
    if not CACHE_DIR.exists():
        return
    files = sorted(CACHE_DIR.iterdir(), key=lambda f: f.stat().st_mtime, reverse=True)
    # .mp3 和 .json 各算一半
    total = sum(1 for f in files if f.suffix == ".mp3")
    if total > CACHE_MAX_FILES:
        for f in files:
            if total <= CACHE_MAX_FILES:
                break
            if f.suffix in (".mp3", ".json"):
                f.unlink(missing_ok=True)
                total -= 1


def _mem_get(key: str) -> Optional[tuple[bytes, list[dict]]]:
    if key in _MEM_CACHE:
        _MEM_CACHE.move_to_end(key)
        return _MEM_CACHE[key]
    return None


def _mem_put(key: str, data: tuple[bytes, list[dict]]):
    _MEM_CACHE[key] = data
    if len(_MEM_CACHE) > _MEM_CACHE_MAX:
        _MEM_CACHE.popitem(last=False)


class TTSService:
    """TTS 语音合成服务"""

    @staticmethod
    def _pitch_to_edge_format(pitch: float) -> str:
        if pitch == 1.0:
            return "+0Hz"
        diff = pitch - 1.0
        hz = int(diff * 100)
        return f"{hz:+d}Hz"

    @staticmethod
    def _rate_to_edge_format(rate: float) -> str:
        percent = int((rate - 1.0) * 100)
        return f"{percent:+d}%"

    @staticmethod
    async def speak(req: TTSSpeakRequest) -> tuple[bytes, list[dict]]:
        """合成语音，返回 (mp3_audio_bytes, word_boundaries)

        缓存路径：内存 LRU → 磁盘缓存 → 合成（连接池复用）
        """
        key = _cache_key(req.input, req.voice, req.pitch, req.rate)

        # 1. 内存缓存
        cached = _mem_get(key)
        if cached is not None:
            return cached

        # 2. 磁盘缓存
        cached = _load_from_disk(key)
        if cached is not None:
            _mem_put(key, cached)
            return cached

        # 3. 合成（使用共享连接池）
        communicate = Communicate(
            req.input,
            req.voice,
            rate=TTSService._rate_to_edge_format(req.rate),
            pitch=TTSService._pitch_to_edge_format(req.pitch),
            connector=_get_connector(),
            connect_timeout=10,
            receive_timeout=60,
        )

        audio_data = bytearray()
        boundaries: list[dict] = []

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.extend(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                boundaries.append({
                    "offset": chunk.get("offset", 0),
                    "duration": chunk.get("duration", 0),
                    "text": chunk.get("text", ""),
                })

        result = (bytes(audio_data), boundaries)

        # 4. 写入缓存
        _save_to_disk(key, result[0], result[1])
        _mem_put(key, result)

        return result

    @staticmethod
    async def get_voices() -> list[dict]:
        """获取所有可用语音列表"""
        voices_data = await list_voices()
        result = []
        for v in voices_data:
            short_name = v.get("ShortName", "")
            locale = v.get("Locale", "")
            name = short_name
            if locale and short_name.startswith(locale):
                suffix = short_name[len(locale) + 1:]
                name = suffix.replace("Neural", "")
            result.append({
                "name": name,
                "id": short_name,
                "lang": locale,
            })
        return result

    @staticmethod
    def clear_cache():
        """手动清除所有缓存"""
        _MEM_CACHE.clear()
        if CACHE_DIR.exists():
            import shutil
            shutil.rmtree(str(CACHE_DIR))
