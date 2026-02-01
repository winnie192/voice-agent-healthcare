from __future__ import annotations

import asyncio
import logging
import re
import uuid
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from src.api.agents.booking_agent import handle_booking
from src.api.agents.intent_classifier import classify_and_extract
from src.api.agents.kb_retrieval import retrieve_knowledge
from src.api.agents.search_agent import web_search
from src.api.agents.synthesizer import synthesize_response

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

MAX_HISTORY_ENTRIES = 12

_SIMPLE_INTENT_RE = re.compile(
    r"^\s*(hi|hello|hey|good\s*(morning|afternoon|evening)|bye|goodbye|see\s*you|thanks|thank\s*you)\s*[.!?]*\s*$",
    re.IGNORECASE,
)

_BOOKING_RE = re.compile(
    r"\b(book|booking|appointment|schedule|reserve|cancel)\b",
    re.IGNORECASE,
)

_QUESTION_RE = re.compile(
    r"\b(what|when|where|how|can|do you|is there|are there|tell me|info)\b",
    re.IGNORECASE,
)


def _is_simple_intent(utterance: str) -> bool:
    return _SIMPLE_INTENT_RE.match(utterance) is not None


def pick_filler_phrase(utterance: str) -> str | None:
    if _is_simple_intent(utterance):
        return None
    if _BOOKING_RE.search(utterance):
        return "Let me check that for you."
    if _QUESTION_RE.search(utterance):
        return "Let me look into that."
    return "One moment."


@dataclass
class BusinessContext:
    business_id: uuid.UUID
    name: str
    location: str
    hours: str
    policies: str


@dataclass
class CallSession:
    business: BusinessContext
    session: AsyncSession
    conversation_history: list[dict[str, str]] = field(default_factory=list)
    booking_draft: dict[str, Any] = field(default_factory=dict)
    booking_completed: bool = False


async def process_utterance(
    call_session: CallSession,
    utterance: str,
) -> AsyncGenerator[str, None]:
    call_session.conversation_history.append({"role": "caller", "content": utterance})

    biz = call_session.business
    biz_id = biz.business_id

    is_simple = _is_simple_intent(utterance)

    recent_history = call_session.conversation_history[-4:]

    if is_simple:
        intent, booking_info = await classify_and_extract(
            utterance, conversation_history=recent_history
        )
        kb_result = None
    else:
        intent_task = classify_and_extract(
            utterance, conversation_history=recent_history
        )
        kb_task = retrieve_knowledge(biz_id, utterance)
        (intent, booking_info), kb_result = await asyncio.gather(intent_task, kb_task)

    if (
        call_session.booking_draft
        and not call_session.booking_completed
        and intent not in ("GOODBYE",)
    ):
        intent = "BOOKING"

    additional_context = ""
    context_section = ""

    if kb_result:
        context_section = f"Relevant knowledge base info:\n{kb_result}"

    if intent == "GREETING":
        pass
    elif intent == "GOODBYE":
        additional_context = "The caller is ending the call. Say goodbye warmly."
    elif intent == "BOOKING":
        booking_result = await handle_booking(
            call_session.session,
            biz_id,
            utterance,
            booking_draft=call_session.booking_draft,
            conversation_history=call_session.conversation_history,
            pre_extracted=booking_info,
        )
        additional_context = f"Booking system response: {booking_result}"
        if "confirmed" in booking_result.lower():
            call_session.booking_completed = True
            call_session.booking_draft = {}
    elif intent == "SEARCH":
        search_result = await web_search(utterance)
        if search_result:
            context_section += f"\n\nWeb search:\n{search_result}"

    if call_session.booking_completed:
        additional_context += (
            "\nNote: A booking was already confirmed earlier in this call. "
            "Do not re-offer booking unless caller explicitly asks."
        )

    full_response_parts: list[str] = []

    trimmed_history = call_session.conversation_history[-MAX_HISTORY_ENTRIES:]

    async for token in synthesize_response(
        business_name=biz.name,
        location=biz.location,
        hours=biz.hours,
        policies=biz.policies,
        intent=intent,
        utterance=utterance,
        additional_context=additional_context,
        context_section=context_section,
        conversation_history=trimmed_history,
    ):
        full_response_parts.append(token)
        yield token

    full_response = "".join(full_response_parts)
    call_session.conversation_history.append(
        {"role": "agent", "content": full_response}
    )
