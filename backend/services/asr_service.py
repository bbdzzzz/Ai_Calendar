import asyncio
import json
import logging
from typing import AsyncGenerator

from funasr import AutoModel

from backend.core.config import settings

logger = logging.getLogger(__name__)

_model = None
_model_lock = asyncio.Lock()


def _get_model():
    global _model
    if _model is None:
        logger.info("加载ASR模型: %s", settings.ASR_MODEL)
        _model = AutoModel(model=settings.ASR_MODEL)
    return _model


class ASRStream:
    def __init__(self):
        self._chunks: list[bytes] = []
        self._model = _get_model()

    def feed(self, audio_bytes: bytes):
        self._chunks.append(audio_bytes)

    def get_partial(self) -> str:
        if not self._chunks:
            return ""
        try:
            import numpy as np

            pcm_data = b"".join(self._chunks)
            audio_np = np.frombuffer(pcm_data, dtype=np.int16).astype(np.float32) / 32768.0
            result = self._model.generate(input=audio_np, batch_size_s=300)
            if result and len(result) > 0:
                return result[0].get("text", "")
        except Exception as e:
            logger.warning("ASR中间识别异常: %s", e)
        return ""

    def finalize(self) -> str:
        if not self._chunks:
            return ""
        try:
            import numpy as np

            pcm_data = b"".join(self._chunks)
            audio_np = np.frombuffer(pcm_data, dtype=np.int16).astype(np.float32) / 32768.0
            result = self._model.generate(input=audio_np, batch_size_s=300)
            if result and len(result) > 0:
                return result[0].get("text", "")
        except Exception as e:
            logger.error("ASR最终识别异常: %s", e)
        return ""


def create_stream() -> ASRStream:
    _get_model()
    return ASRStream()
