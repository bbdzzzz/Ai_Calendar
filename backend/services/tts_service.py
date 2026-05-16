import asyncio
import logging
from typing import AsyncGenerator

import edge_tts

from backend.core.config import settings

logger = logging.getLogger(__name__)


async def stream_tts(text: str, voice: str | None = None) -> AsyncGenerator[bytes, None]:
    communicate = edge_tts.Communicate(text, voice or settings.TTS_VOICE)
    stream = communicate.stream()
    async for chunk in stream:
        if chunk["type"] == "audio":
            yield chunk["data"]
