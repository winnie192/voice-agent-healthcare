from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.api.agents.orchestrator import (
    BusinessContext,
    CallSession,
    _is_simple_intent,
    pick_filler_phrase,
    process_utterance,
)


class TestIsSimpleIntent:
    @pytest.mark.parametrize(
        "utterance",
        [
            "hi",
            "Hello!",
            "hey",
            "good morning",
            "Good Afternoon!",
            "bye",
            "goodbye",
            "see you",
            "thanks",
            "thank you",
        ],
    )
    def test_matches_greetings_and_goodbyes(self, utterance: str) -> None:
        assert _is_simple_intent(utterance) is True

    @pytest.mark.parametrize(
        "utterance",
        [
            "I want to book a consultation",
            "What are your hours?",
            "Can you help me find a pharmacy?",
            "hello I need an appointment",
            "hi there can you help me",
        ],
    )
    def test_rejects_substantive_queries(self, utterance: str) -> None:
        assert _is_simple_intent(utterance) is False


class TestConversationHistoryTrimming:
    @pytest.mark.asyncio
    @patch("src.api.agents.orchestrator.classify_and_extract")
    @patch("src.api.agents.orchestrator.retrieve_knowledge")
    @patch("src.api.agents.orchestrator.synthesize_response")
    async def test_conversation_history_trimmed_to_6_turns(
        self,
        mock_synthesize: MagicMock,
        mock_kb: AsyncMock,
        mock_classify: AsyncMock,
    ) -> None:
        mock_classify.return_value = ("GREETING", None)
        mock_kb.return_value = None

        captured_history: list[dict[str, str]] | None = None

        async def fake_synthesize(**kwargs):  # type: ignore[no-untyped-def]
            nonlocal captured_history
            captured_history = kwargs.get("conversation_history")
            return
            yield  # make it an async generator

        mock_synthesize.side_effect = fake_synthesize

        context = BusinessContext(
            business_id=uuid.uuid4(),
            name="Test Clinic",
            location="123 St",
            hours="9-5",
            policies="None",
        )
        session = CallSession(
            business=context,
            session=MagicMock(),
        )
        for i in range(20):
            session.conversation_history.append(
                {"role": "caller", "content": f"message {i}"}
            )

        async for _ in process_utterance(session, "hello"):
            pass

        assert captured_history is not None
        assert len(captured_history) <= 12


class TestBookingCompletedFlag:
    @pytest.mark.asyncio
    @patch("src.api.agents.orchestrator.classify_and_extract")
    @patch("src.api.agents.orchestrator.retrieve_knowledge")
    @patch("src.api.agents.orchestrator.handle_booking")
    @patch("src.api.agents.orchestrator.synthesize_response")
    async def test_booking_completed_set_on_confirmation(
        self,
        mock_synthesize: MagicMock,
        mock_booking: AsyncMock,
        mock_kb: AsyncMock,
        mock_classify: AsyncMock,
    ) -> None:
        mock_classify.return_value = ("BOOKING", {"action": "schedule"})
        mock_kb.return_value = None
        mock_booking.return_value = "Appointment confirmed for Monday at 10am."

        async def fake_synthesize(**kwargs):  # type: ignore[no-untyped-def]
            return
            yield

        mock_synthesize.side_effect = fake_synthesize

        context = BusinessContext(
            business_id=uuid.uuid4(),
            name="Test Clinic",
            location="123 St",
            hours="9-5",
            policies="None",
        )
        session = CallSession(business=context, session=MagicMock())

        async for _ in process_utterance(session, "Book me for Monday"):
            pass

        assert session.booking_completed is True
        assert session.booking_draft == {}

    @pytest.mark.asyncio
    @patch("src.api.agents.orchestrator.classify_and_extract")
    @patch("src.api.agents.orchestrator.retrieve_knowledge")
    @patch("src.api.agents.orchestrator.synthesize_response")
    async def test_booking_completed_prevents_sticky_intent(
        self,
        mock_synthesize: MagicMock,
        mock_kb: AsyncMock,
        mock_classify: AsyncMock,
    ) -> None:
        mock_classify.return_value = ("INQUIRY", None)
        mock_kb.return_value = None

        captured_intent: str | None = None

        async def fake_synthesize(**kwargs):  # type: ignore[no-untyped-def]
            nonlocal captured_intent
            captured_intent = kwargs.get("intent")
            return
            yield

        mock_synthesize.side_effect = fake_synthesize

        context = BusinessContext(
            business_id=uuid.uuid4(),
            name="Test Clinic",
            location="123 St",
            hours="9-5",
            policies="None",
        )
        session = CallSession(business=context, session=MagicMock())
        session.booking_draft = {"action": "schedule"}
        session.booking_completed = True

        async for _ in process_utterance(session, "What services do you offer?"):
            pass

        assert captured_intent == "INQUIRY"

    @pytest.mark.asyncio
    @patch("src.api.agents.orchestrator.classify_and_extract")
    @patch("src.api.agents.orchestrator.retrieve_knowledge")
    @patch("src.api.agents.orchestrator.synthesize_response")
    async def test_booking_completed_adds_context_note(
        self,
        mock_synthesize: MagicMock,
        mock_kb: AsyncMock,
        mock_classify: AsyncMock,
    ) -> None:
        mock_classify.return_value = ("INQUIRY", None)
        mock_kb.return_value = None

        captured_context: str | None = None

        async def fake_synthesize(**kwargs):  # type: ignore[no-untyped-def]
            nonlocal captured_context
            captured_context = kwargs.get("additional_context")
            return
            yield

        mock_synthesize.side_effect = fake_synthesize

        context = BusinessContext(
            business_id=uuid.uuid4(),
            name="Test Clinic",
            location="123 St",
            hours="9-5",
            policies="None",
        )
        session = CallSession(business=context, session=MagicMock())
        session.booking_completed = True

        async for _ in process_utterance(session, "What services do you offer?"):
            pass

        assert captured_context is not None
        assert "already confirmed" in captured_context


class TestPickFillerPhrase:
    @pytest.mark.parametrize(
        "utterance,expected",
        [
            ("I want to book an appointment", "Let me check that for you."),
            ("Can I schedule a cleaning?", "Let me check that for you."),
            ("I need to cancel my booking", "Let me check that for you."),
        ],
    )
    def test_filler_phrase_for_booking_keyword(
        self, utterance: str, expected: str
    ) -> None:
        assert pick_filler_phrase(utterance) == expected

    @pytest.mark.parametrize(
        "utterance,expected",
        [
            ("What are your hours?", "Let me look into that."),
            ("Can you tell me about your services?", "Let me look into that."),
            ("How much does a cleaning cost?", "Let me look into that."),
        ],
    )
    def test_filler_phrase_for_question(self, utterance: str, expected: str) -> None:
        assert pick_filler_phrase(utterance) == expected

    @pytest.mark.parametrize(
        "utterance",
        [
            "hi",
            "Hello!",
            "hey",
            "good morning",
            "bye",
            "goodbye",
            "thanks",
        ],
    )
    def test_no_filler_for_greeting(self, utterance: str) -> None:
        assert pick_filler_phrase(utterance) is None

    def test_default_filler_for_unknown(self) -> None:
        assert pick_filler_phrase("something random blah") == "One moment."
