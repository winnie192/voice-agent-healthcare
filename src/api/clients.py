from __future__ import annotations

from openai import AsyncOpenAI

from src.api.config import settings

_openai_client: AsyncOpenAI | None = None


def get_openai_client() -> AsyncOpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _openai_client
