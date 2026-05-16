import logging
from typing import Any

from openai import AsyncOpenAI

from backend.core.config import settings

logger = logging.getLogger(__name__)

_client: AsyncOpenAI | None = None


def get_llm_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        api_key = settings.LLM_API_KEY or "sk-placeholder"
        base_url = settings.LLM_BASE_URL.rstrip("/")
        if not base_url.endswith("/v1"):
            base_url += "/v1"
        _client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )
    return _client


async def chat_completion(
    messages: list[dict],
    tools: list[dict] | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> Any:
    client = get_llm_client()
    kwargs: dict[str, Any] = {
        "model": settings.LLM_MODEL,
        "messages": messages,
        "temperature": temperature or settings.LLM_TEMPERATURE,
        "max_tokens": max_tokens or settings.LLM_MAX_TOKENS,
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"
    response = await client.chat.completions.create(**kwargs)
    return response
