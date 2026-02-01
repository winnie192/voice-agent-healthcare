from __future__ import annotations

import uuid
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

import pytest

from src.api.agents.orchestrator import BusinessContext
from src.api.voice.twilio_handler import TwilioCallHandler

if TYPE_CHECKING:
    from httpx import AsyncClient


@pytest.mark.asyncio
async def test_twilio_incoming_returns_twiml(client: AsyncClient) -> None:
    resp = await client.post(
        "/voice/twilio/incoming",
        data={"To": "+15551234567"},
        headers={
            "host": "example.com",
            "content-type": "application/x-www-form-urlencoded",
        },
    )
    assert resp.status_code == 200
    assert "application/xml" in resp.headers["content-type"]
    body = resp.text
    assert "wss://example.com/voice/ws/+15551234567" in body
    assert "<Stream" in body
    assert "<Connect" in body


@pytest.mark.asyncio
async def test_twilio_incoming_missing_to(client: AsyncClient) -> None:
    resp = await client.post(
        "/voice/twilio/incoming",
        data={},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200
    body = resp.text
    assert "/voice/ws/" in body


@pytest.mark.asyncio
async def test_twilio_incoming_uses_host_header(client: AsyncClient) -> None:
    resp = await client.post(
        "/voice/twilio/incoming",
        data={"To": "+15550000000"},
        headers={
            "host": "my-domain.io",
            "content-type": "application/x-www-form-urlencoded",
        },
    )
    assert "wss://my-domain.io/voice/ws/+15550000000" in resp.text


@pytest.mark.asyncio
async def test_twilio_call_handler_init() -> None:
    mock_ws = AsyncMock()
    mock_session = AsyncMock()
    biz_id = uuid.uuid4()
    context = BusinessContext(
        business_id=biz_id,
        name="Test",
        location="123 Main",
        hours="9-5",
        policies="None",
    )

    with (
        patch("src.api.voice.twilio_handler.DeepgramSTT"),
        patch("src.api.voice.twilio_handler.TTSWithFallback"),
    ):
        handler = TwilioCallHandler(
            twilio_ws=mock_ws,
            business_context=context,
            db_session=mock_session,
        )

    assert handler._call_session.business.business_id == biz_id
    assert handler._call_session.business.name == "Test"


@pytest.mark.asyncio
async def test_twilio_call_handler_handle_stop_event() -> None:
    import json

    mock_ws = AsyncMock()
    stop_msg = json.dumps({"event": "stop"})
    mock_ws.__aiter__ = lambda self: self
    mock_ws.__anext__ = AsyncMock(side_effect=[stop_msg, StopAsyncIteration])

    mock_session = AsyncMock()
    context = BusinessContext(
        business_id=uuid.uuid4(),
        name="Test",
        location="",
        hours="",
        policies="",
    )

    mock_stt = AsyncMock()
    mock_stt.connect = AsyncMock()
    mock_stt.close = AsyncMock()
    mock_stt.get_transcripts = AsyncMock(
        return_value=AsyncMock(
            __aiter__=lambda s: s, __anext__=AsyncMock(side_effect=StopAsyncIteration)
        )
    )
    mock_stt.wait_for_speech = AsyncMock(side_effect=Exception("stop"))

    mock_tts = AsyncMock()
    mock_tts.connect = AsyncMock()
    mock_tts.close = AsyncMock()
    mock_tts.get_audio = AsyncMock(
        return_value=AsyncMock(
            __aiter__=lambda s: s, __anext__=AsyncMock(side_effect=StopAsyncIteration)
        )
    )

    with (
        patch("src.api.voice.twilio_handler.DeepgramSTT", return_value=mock_stt),
        patch("src.api.voice.twilio_handler.TTSWithFallback", return_value=mock_tts),
    ):
        handler = TwilioCallHandler(
            twilio_ws=mock_ws,
            business_context=context,
            db_session=mock_session,
        )
        await handler.handle()

    mock_stt.connect.assert_awaited_once()
    mock_tts.connect.assert_awaited_once()
    mock_stt.close.assert_awaited_once()
    mock_tts.close.assert_awaited_once()
