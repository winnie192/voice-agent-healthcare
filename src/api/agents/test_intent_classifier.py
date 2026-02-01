from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.api.agents.intent_classifier import classify_and_extract


class _FakeChoice:
    def __init__(self, content: str) -> None:
        self.message = type("M", (), {"content": content})()


class _FakeResponse:
    def __init__(self, content: str) -> None:
        self.choices = [_FakeChoice(content)]


class TestClassifyAndExtract:
    @pytest.mark.asyncio
    async def test_booking_intent_returns_intent_and_booking(self) -> None:
        payload = (
            '{"intent": "BOOKING", "booking": '
            '{"action": "schedule", "service_name": "Consultation", '
            '"preferred_date": null, "preferred_time": null, '
            '"customer_name": null, "customer_phone": null}}'
        )
        api_response = _FakeResponse(payload)
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = api_response

        with patch(
            "src.api.agents.intent_classifier.get_openai_client",
            return_value=mock_client,
        ):
            intent, booking = await classify_and_extract(
                "I want to book a consultation"
            )

        assert intent == "BOOKING"
        assert booking is not None
        assert booking["service_name"] == "Consultation"

    @pytest.mark.asyncio
    async def test_non_booking_intent_returns_none_booking(self) -> None:
        api_response = _FakeResponse('{"intent": "GREETING", "booking": null}')
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = api_response

        with patch(
            "src.api.agents.intent_classifier.get_openai_client",
            return_value=mock_client,
        ):
            intent, booking = await classify_and_extract("hello")

        assert intent == "GREETING"
        assert booking is None

    @pytest.mark.asyncio
    async def test_invalid_intent_falls_back_to_unknown(self) -> None:
        api_response = _FakeResponse('{"intent": "INVALID", "booking": null}')
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = api_response

        with patch(
            "src.api.agents.intent_classifier.get_openai_client",
            return_value=mock_client,
        ):
            intent, booking = await classify_and_extract("asdfghjkl")

        assert intent == "UNKNOWN"

    @pytest.mark.asyncio
    async def test_conversation_history_included_in_prompt(self) -> None:
        api_response = _FakeResponse('{"intent": "INQUIRY", "booking": null}')
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = api_response

        with patch(
            "src.api.agents.intent_classifier.get_openai_client",
            return_value=mock_client,
        ):
            history = [
                {"role": "caller", "content": "Tell me about physical therapy"},
                {"role": "agent", "content": "We offer physical therapy sessions."},
            ]
            intent, _ = await classify_and_extract(
                "How much does it cost?", conversation_history=history
            )

        assert intent == "INQUIRY"
        call_args = mock_client.chat.completions.create.call_args
        user_msg = call_args.kwargs["messages"][1]["content"]
        assert "physical therapy" in user_msg
