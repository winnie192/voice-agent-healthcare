from __future__ import annotations

import httpx

from src.api.config import settings


async def web_search(query: str) -> str:
    if not settings.serper_api_key:
        return "Web search is not configured."

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": settings.serper_api_key, "Content-Type": "application/json"},
            json={"q": query, "num": 3},
        )
        response.raise_for_status()
        data = response.json()

    results: list[str] = []
    for item in data.get("organic", [])[:3]:
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        results.append(f"{title}: {snippet}")

    return "\n".join(results) if results else "No search results found."
