from __future__ import annotations

from collections.abc import AsyncGenerator

from src.api.clients import get_openai_client
from src.api.prompts.synthesizer import SYNTHESIZER_SYSTEM, SYNTHESIZER_USER


async def synthesize_response(
    business_name: str,
    location: str,
    hours: str,
    policies: str,
    intent: str,
    utterance: str,
    additional_context: str = "",
    context_section: str = "",
    conversation_history: list[dict[str, str]] | None = None,
) -> AsyncGenerator[str, None]:
    client = get_openai_client()

    system_msg = SYNTHESIZER_SYSTEM.format(
        business_name=business_name,
        location=location or "Not specified",
        hours=hours or "Not specified",
        policies=policies or "None specified",
        context_section=context_section,
    )
    user_msg = SYNTHESIZER_USER.format(
        intent=intent,
        utterance=utterance,
        additional_context=additional_context,
    )

    messages: list[dict[str, str]] = [{"role": "system", "content": system_msg}]
    # Include conversation history for context
    if conversation_history:
        for turn in conversation_history[
            :-1
        ]:  # exclude current utterance (already in user_msg)
            role = "user" if turn["role"] == "caller" else "assistant"
            messages.append({"role": role, "content": turn["content"]})
    messages.append({"role": "user", "content": user_msg})

    stream = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=300,
        stream=True,
    )

    async for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content
