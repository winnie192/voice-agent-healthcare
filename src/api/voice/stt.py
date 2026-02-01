from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncGenerator

import websockets

from src.api.config import settings

logger = logging.getLogger(__name__)

DEEPGRAM_WS_URL = "wss://api.deepgram.com/v1/listen"


class DeepgramSTT:
    _KEEPALIVE_INTERVAL = 8

    def __init__(self) -> None:
        self._ws: websockets.WebSocketClientProtocol | None = None
        self._transcript_queue: asyncio.Queue[str] = asyncio.Queue()
        self._speech_started: asyncio.Event = asyncio.Event()
        self._running = False
        self._audio_buffer = bytearray()
        self._sample_rate = 48000
        self._buffer_duration = 0.25  # seconds
        self._keepalive_task: asyncio.Task[None] | None = None

    async def connect(self, sample_rate: int = 48000) -> None:
        params = (
            f"?encoding=linear16&sample_rate={sample_rate}&channels=1"
            "&model=nova-2&punctuate=true&interim_results=true"
            "&endpointing=200&vad_events=true"
        )
        headers = {"Authorization": f"Token {settings.deepgram_api_key}"}
        full_url = f"{DEEPGRAM_WS_URL}{params}"
        logger.info("[Deepgram] Connecting to: %s", full_url)
        self._ws = await websockets.connect(
            full_url,
            additional_headers=headers,
        )
        self._sample_rate = sample_rate
        self._audio_buffer = bytearray()
        self._running = True
        asyncio.create_task(self._receive_loop())
        self._keepalive_task = asyncio.create_task(self._keepalive_loop())

    async def _keepalive_loop(self) -> None:
        while self._running and self._ws:
            try:
                await asyncio.sleep(self._KEEPALIVE_INTERVAL)
                if self._ws and self._running:
                    msg = {"type": "KeepAlive"}
                    await self._ws.send(json.dumps(msg))
            except Exception:
                break

    async def _receive_loop(self) -> None:
        if not self._ws:
            return
        try:
            async for message in self._ws:
                data = json.loads(message)
                msg_type = data.get("type", "unknown")
                print(f"[Deepgram] type={msg_type}")

                if msg_type == "SpeechStarted":
                    self._speech_started.set()
                    continue

                if msg_type == "Results":
                    is_final = data.get("is_final", False)
                    channel = data.get("channel", {})
                    alternatives = channel.get("alternatives", [])
                    transcript = (
                        alternatives[0].get("transcript", "") if alternatives else ""
                    )
                    print(f"[Deepgram] is_final={is_final} transcript='{transcript}'")
                    if transcript.strip() and is_final:
                        await self._transcript_queue.put(transcript.strip())

                if msg_type == "Error":
                    print(f"[Deepgram] ERROR: {data}")
        except websockets.exceptions.ConnectionClosed as e:
            print(f"[Deepgram] connection closed: {e}")
        except Exception as e:
            print(f"[Deepgram] receive error: {e}")
        finally:
            self._running = False

    async def wait_for_speech(self) -> None:
        self._speech_started.clear()
        await self._speech_started.wait()

    def clear_speech_flag(self) -> None:
        self._speech_started.clear()

    async def send_audio(self, pcm_bytes: bytes) -> None:
        if self._ws and self._running:
            await self._ws.send(pcm_bytes)

    async def get_transcripts(self) -> AsyncGenerator[str, None]:
        while self._running or not self._transcript_queue.empty():
            try:
                transcript = await asyncio.wait_for(
                    self._transcript_queue.get(), timeout=0.1
                )
                yield transcript
            except asyncio.TimeoutError:
                continue

    async def close(self) -> None:
        self._running = False
        if self._keepalive_task:
            self._keepalive_task.cancel()
        if self._ws:
            await self._ws.close()
