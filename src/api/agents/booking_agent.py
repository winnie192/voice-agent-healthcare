from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.clients import get_openai_client
from src.api.db.queries import (
    create_booking,
    get_booking_rules,
    get_services_for_business,
)
from src.api.prompts.booking import BOOKING_EXTRACTION_SYSTEM, BOOKING_EXTRACTION_USER


def _build_conversation_context(
    conversation_history: list[dict[str, str]],
    current_utterance: str,
    max_entries: int = 6,
) -> str:
    recent = conversation_history[-max_entries:]
    lines = [f"{entry['role']}: {entry['content']}" for entry in recent]
    lines.append(f"caller: {current_utterance}")
    return "\n".join(lines)


async def extract_booking_info(utterance: str) -> dict[str, Any]:
    client = get_openai_client()
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": BOOKING_EXTRACTION_SYSTEM},
            {
                "role": "user",
                "content": BOOKING_EXTRACTION_USER.format(utterance=utterance),
            },
        ],
        temperature=0,
        max_tokens=200,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "{}"
    return json.loads(content)


async def handle_booking(
    session: AsyncSession,
    business_id: uuid.UUID,
    utterance: str,
    booking_draft: dict[str, Any] | None = None,
    conversation_history: list[dict[str, str]] | None = None,
    pre_extracted: dict[str, Any] | None = None,
) -> str:
    if booking_draft is None:
        booking_draft = {}

    if pre_extracted is not None:
        info = pre_extracted
    else:
        context = utterance
        if conversation_history:
            context = _build_conversation_context(conversation_history, utterance)
        info = await extract_booking_info(context)
    action = info.get("action", "info")

    for key in (
        "service_name",
        "preferred_date",
        "preferred_time",
        "customer_name",
        "customer_phone",
    ):
        value = info.get(key)
        if value:
            booking_draft[key] = value

    if booking_draft:
        action = "schedule"

    if action == "info":
        services = await get_services_for_business(session, business_id)
        if not services:
            return "This business hasn't set up any bookable services yet."
        service_list = ", ".join(
            f"{s.name} ({s.duration_minutes} min)" for s in services
        )
        return f"Available services: {service_list}. Which would you like to book?"

    if action == "schedule":
        service_name = booking_draft.get("service_name")
        if not service_name:
            return "Which service would you like to book?"

        services = await get_services_for_business(session, business_id)
        matched = next(
            (s for s in services if s.name.lower() == service_name.lower()), None
        )
        if not matched:
            service_list = ", ".join(s.name for s in services)
            return f"I couldn't find that service. Available: {service_list}"

        preferred_date = booking_draft.get("preferred_date")
        preferred_time = booking_draft.get("preferred_time")
        customer_name = booking_draft.get("customer_name")
        customer_phone = booking_draft.get("customer_phone")

        missing: list[str] = []
        if not preferred_date:
            missing.append("preferred date")
        if not preferred_time:
            missing.append("preferred time")
        if not customer_name:
            missing.append("your name")

        if missing:
            return f"To complete the booking, I need: {', '.join(missing)}."

        start = datetime.fromisoformat(f"{preferred_date}T{preferred_time}:00+00:00")
        end = start + timedelta(minutes=matched.duration_minutes)

        booking = await create_booking(
            session,
            business_id=business_id,
            service_id=matched.id,
            customer_name=customer_name,
            customer_phone=customer_phone or "",
            start_time=start,
            end_time=end,
            status="confirmed",
        )
        booking_draft.clear()
        return f"Your {matched.name} appointment is confirmed for {preferred_date} at {preferred_time}."

    if action == "cancel":
        return "To cancel, I'll need your name and the appointment date. Could you provide those?"

    return "I can help with booking. What would you like to do?"
