from __future__ import annotations

import json
from typing import Any

from src.api.clients import get_openai_client
from src.api.prompts.intent import (
    INTENT_CLASSIFIER_SYSTEM,
    INTENT_CLASSIFIER_USER,
    UNIFIED_INTENT_SYSTEM,
    UNIFIED_INTENT_USER,
)

VALID_INTENTS = {"BOOKING", "INQUIRY", "SEARCH", "GREETING", "GOODBYE", "UNKNOWN"}


async def classify_intent(utterance: str) -> str:
    client = get_openai_client()
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": INTENT_CLASSIFIER_SYSTEM},
            {
                "role": "user",
                "content": INTENT_CLASSIFIER_USER.format(utterance=utterance),
            },
        ],
        temperature=0,
        max_tokens=20,
    )
    intent = (response.choices[0].message.content or "UNKNOWN").strip().upper()
    return intent if intent in VALID_INTENTS else "UNKNOWN"


async def classify_and_extract(
    utterance: str,
    conversation_history: list[dict[str, str]] | None = None,
) -> tuple[str, dict[str, Any] | None]:
    client = get_openai_client()

    history_text = ""
    if conversation_history:
        lines = []
        for turn in conversation_history:
            role_label = "Caller" if turn["role"] == "caller" else "Agent"
            lines.append(f"{role_label}: {turn['content']}")
        history_text = "\n".join(lines)

    user_content = UNIFIED_INTENT_USER.format(utterance=utterance, history=history_text)

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": UNIFIED_INTENT_SYSTEM},
            {"role": "user", "content": user_content},
        ],
        temperature=0,
        max_tokens=200,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "{}"
    data = json.loads(content)
    intent = str(data.get("intent", "UNKNOWN")).strip().upper()
    if intent not in VALID_INTENTS:
        intent = "UNKNOWN"
    booking = data.get("booking")
    return intent, booking
