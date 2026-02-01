from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest

from src.api.voice.tts import DeepgramTTS, TTSWithFallback


@pytest.mark.asyncio
async def test_deepgram_tts_send_text_format() -> None:
    tts = DeepgramTTS()
    mock_ws = AsyncMock()
    tts._ws = mock_ws
    tts._running = True

    await tts.send_text("Hello world")

    mock_ws.send.assert_awaited_once()
    sent = json.loads(mock_ws.send.call_args[0][0])
    assert sent == {"type": "Speak", "text": "Hello world"}


@pytest.mark.asyncio
async def test_deepgram_tts_flush_format() -> None:
    tts = DeepgramTTS()
    mock_ws = AsyncMock()
    tts._ws = mock_ws
    tts._running = True

    await tts.flush()

    mock_ws.send.assert_awaited_once()
    sent = json.loads(mock_ws.send.call_args[0][0])
    assert sent == {"type": "Flush"}


@pytest.mark.asyncio
async def test_tts_with_fallback_uses_primary_on_success() -> None:
    mock_primary = AsyncMock()
    mock_fallback = AsyncMock()

    with patch(
        "src.api.voice.tts._build_provider_pair",
        return_value=(mock_primary, mock_fallback),
    ):
        tts = TTSWithFallback()

    await tts.connect()

    mock_primary.connect.assert_awaited_once()
    mock_fallback.connect.assert_not_awaited()
    assert tts._active is mock_primary


@pytest.mark.asyncio
async def test_tts_with_fallback_switches_on_primary_failure() -> None:
    mock_primary = AsyncMock()
    mock_primary.connect.side_effect = ConnectionError("refused")
    mock_fallback = AsyncMock()

    with patch(
        "src.api.voice.tts._build_provider_pair",
        return_value=(mock_primary, mock_fallback),
    ):
        tts = TTSWithFallback()

    await tts.connect()

    mock_primary.connect.assert_awaited_once()
    mock_fallback.connect.assert_awaited_once()
    assert tts._active is mock_fallback


@pytest.mark.asyncio
async def test_tts_with_fallback_delegates_send_text() -> None:
    mock_primary = AsyncMock()
    mock_fallback = AsyncMock()

    with patch(
        "src.api.voice.tts._build_provider_pair",
        return_value=(mock_primary, mock_fallback),
    ):
        tts = TTSWithFallback()

    await tts.connect()
    await tts.send_text("test")

    mock_primary.send_text.assert_awaited_once_with("test")


@pytest.mark.asyncio
async def test_deepgram_tts_interrupt_clears_queue() -> None:
    tts = DeepgramTTS()
    mock_ws = AsyncMock()
    tts._ws = mock_ws
    tts._running = True
    await tts._audio_queue.put(b"audio")
    await tts._audio_queue.put(b"more")

    await tts.interrupt()

    assert tts._audio_queue.empty()
