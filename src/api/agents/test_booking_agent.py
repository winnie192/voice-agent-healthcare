from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from src.api.agents.booking_agent import _build_conversation_context, handle_booking


@dataclass
class FakeService:
    id: uuid.UUID
    name: str
    duration_minutes: int


BUSINESS_ID = uuid.uuid4()
CONSULTATION = FakeService(id=uuid.uuid4(), name="Consultation", duration_minutes=30)


def _make_extraction(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    base: dict[str, Any] = {
        "action": "schedule",
        "service_name": None,
        "preferred_date": None,
        "preferred_time": None,
        "customer_name": None,
        "customer_phone": None,
    }
    if overrides:
        base.update(overrides)
    return base


class TestBuildConversationContext:
    def test_includes_recent_entries_and_current_utterance(self) -> None:
        history = [
            {"role": "caller", "content": "Hi"},
            {"role": "agent", "content": "Hello"},
        ]
        result = _build_conversation_context(history, "I want a consultation")
        assert "caller: Hi" in result
        assert "agent: Hello" in result
        assert "caller: I want a consultation" in result

    def test_limits_to_max_entries(self) -> None:
        history = [{"role": "caller", "content": f"msg{i}"} for i in range(10)]
        result = _build_conversation_context(history, "latest", max_entries=2)
        assert "msg8" in result
        assert "msg9" in result
        assert "msg0" not in result


class TestHandleBookingPreExtracted:
    @pytest.mark.asyncio
    async def test_skips_extract_when_pre_extracted_given(self) -> None:
        draft: dict[str, Any] = {}
        session = AsyncMock()
        pre_extracted = {
            "action": "schedule",
            "service_name": "Consultation",
            "preferred_date": None,
            "preferred_time": None,
            "customer_name": None,
            "customer_phone": None,
        }

        with (
            patch("src.api.agents.booking_agent.extract_booking_info") as mock_extract,
            patch(
                "src.api.agents.booking_agent.get_services_for_business",
                return_value=[CONSULTATION],
            ),
        ):
            await handle_booking(
                session,
                BUSINESS_ID,
                "I want a consultation",
                booking_draft=draft,
                pre_extracted=pre_extracted,
            )
            mock_extract.assert_not_called()
            assert draft["service_name"] == "Consultation"


class TestHandleBookingDraftAccumulation:
    @pytest.mark.asyncio
    async def test_accumulates_fields_across_turns(self) -> None:
        draft: dict[str, Any] = {}
        session = AsyncMock()

        with (
            patch("src.api.agents.booking_agent.extract_booking_info") as mock_extract,
            patch(
                "src.api.agents.booking_agent.get_services_for_business",
                return_value=[CONSULTATION],
            ),
        ):
            mock_extract.return_value = _make_extraction(
                {"service_name": "Consultation"}
            )
            result = await handle_booking(
                session, BUSINESS_ID, "I want a consultation", booking_draft=draft
            )
            assert "preferred date" in result
            assert draft["service_name"] == "Consultation"

            mock_extract.return_value = _make_extraction(
                {"preferred_date": "2026-03-01", "preferred_time": "14:00"}
            )
            result = await handle_booking(
                session, BUSINESS_ID, "tomorrow at 2pm", booking_draft=draft
            )
            assert "your name" in result
            assert draft["preferred_date"] == "2026-03-01"
            assert draft["service_name"] == "Consultation"

    @pytest.mark.asyncio
    async def test_draft_cleared_after_successful_booking(self) -> None:
        draft: dict[str, Any] = {
            "service_name": "Consultation",
            "preferred_date": "2026-03-01",
            "preferred_time": "14:00",
        }
        session = AsyncMock()

        with (
            patch("src.api.agents.booking_agent.extract_booking_info") as mock_extract,
            patch(
                "src.api.agents.booking_agent.get_services_for_business",
                return_value=[CONSULTATION],
            ),
            patch(
                "src.api.agents.booking_agent.create_booking",
                return_value=AsyncMock(),
            ),
        ):
            mock_extract.return_value = _make_extraction({"customer_name": "John"})
            result = await handle_booking(
                session, BUSINESS_ID, "my name is John", booking_draft=draft
            )
            assert "confirmed" in result
            assert draft == {}

    @pytest.mark.asyncio
    async def test_missing_fields_identified_from_partial_draft(self) -> None:
        draft: dict[str, Any] = {"service_name": "Consultation"}
        session = AsyncMock()

        with (
            patch("src.api.agents.booking_agent.extract_booking_info") as mock_extract,
            patch(
                "src.api.agents.booking_agent.get_services_for_business",
                return_value=[CONSULTATION],
            ),
        ):
            mock_extract.return_value = _make_extraction({"preferred_time": "10:00"})
            result = await handle_booking(
                session, BUSINESS_ID, "at 10am", booking_draft=draft
            )
            assert "preferred date" in result
            assert "your name" in result
            assert "preferred time" not in result
