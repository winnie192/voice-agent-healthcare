from __future__ import annotations

import asyncio
import base64
import json
import logging
from collections.abc import AsyncGenerator
from typing import Protocol, runtime_checkable

import websockets

from src.api.config import settings

logger = logging.getLogger(__name__)

ELEVENLABS_WS_URL = "wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input"
DEEPGRAM_WS_URL = (
    "wss://api.deepgram.com/v1/speak?encoding=mulaw&sample_rate=8000&model={model}"
)


@runtime_checkable
class TTSProvider(Protocol):
    async def connect(self) -> None: ...
    async def send_text(self, text: str) -> None: ...
    async def flush(self) -> None: ...
    async def interrupt(self) -> None: ...
    def get_audio(self) -> AsyncGenerator[bytes, None]: ...
    async def close(self) -> None: ...


class ElevenLabsTTS:
    def __init__(self) -> None:
        self._ws: websockets.WebSocketClientProtocol | None = None
        self._audio_queue: asyncio.Queue[bytes] = asyncio.Queue()
        self._running = False
        self._reconnect_task: asyncio.Task[None] | None = None

    async def _open_ws(self) -> websockets.WebSocketClientProtocol:
        url = ELEVENLABS_WS_URL.format(voice_id=settings.elevenlabs_voice_id)
        model = settings.elevenlabs_model_id
        params = f"?model_id={model}&output_format=ulaw_8000"
        ws = await websockets.connect(f"{url}{params}")
        init_msg = {
            "text": " ",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
            "xi_api_key": settings.elevenlabs_api_key,
        }
        await ws.send(json.dumps(init_msg))
        return ws

    async def connect(self) -> None:
        self._ws = await self._open_ws()
        self._running = True
        asyncio.create_task(self._receive_loop())

    async def _receive_loop(self) -> None:
        if not self._ws:
            return
        try:
            async for message in self._ws:
                data = json.loads(message)
                if "error" in data or "message" in data:
                    logger.error("ElevenLabs error: %s", data)
                audio_b64 = data.get("audio")
                if audio_b64:
                    audio_bytes = base64.b64decode(audio_b64)
                    await self._audio_queue.put(audio_bytes)
                if data.get("isFinal"):
                    self._start_background_reconnect()
                    return
        except websockets.exceptions.ConnectionClosed:
            self._start_background_reconnect()
        except Exception as e:
            logger.error("TTS receive error: %s", e)
            self._start_background_reconnect()

    def _start_background_reconnect(self) -> None:
        if self._reconnect_task is None or self._reconnect_task.done():
            self._reconnect_task = asyncio.create_task(self._reconnect())

    async def _reconnect(self) -> None:
        try:
            if self._ws:
                await self._ws.close()
        except Exception:
            pass
        self._ws = await self._open_ws()
        asyncio.create_task(self._receive_loop())

    async def _ensure_connected(self) -> None:
        if self._reconnect_task is not None:
            await self._reconnect_task
            self._reconnect_task = None

    async def send_text(self, text: str) -> None:
        await self._ensure_connected()
        if self._ws and self._running:
            msg = {"text": text, "try_trigger_generation": True}
            try:
                await self._ws.send(json.dumps(msg))
            except Exception as e:
                logger.error("TTS send_text failed: %s", e)

    async def flush(self) -> None:
        await self._ensure_connected()
        if self._ws and self._running:
            msg = {"text": ""}
            await self._ws.send(json.dumps(msg))

    async def interrupt(self) -> None:
        while not self._audio_queue.empty():
            try:
                self._audio_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        if self._ws and self._running:
            await self._ws.close()
            await self.connect()

    async def get_audio(self) -> AsyncGenerator[bytes, None]:
        while True:
            if not self._running and self._audio_queue.empty():
                break
            try:
                audio = await asyncio.wait_for(self._audio_queue.get(), timeout=0.5)
                yield audio
            except asyncio.TimeoutError:
                continue

    async def close(self) -> None:
        self._running = False
        if self._ws:
            await self._ws.close()


class DeepgramTTS:
    _KEEPALIVE_INTERVAL = 8

    def __init__(self) -> None:
        self._ws: websockets.WebSocketClientProtocol | None = None
        self._audio_queue: asyncio.Queue[bytes] = asyncio.Queue()
        self._running = False
        self._keepalive_task: asyncio.Task[None] | None = None
        self._reconnect_task: asyncio.Task[None] | None = None

    async def _open_ws(self) -> websockets.WebSocketClientProtocol:
        url = DEEPGRAM_WS_URL.format(model=settings.deepgram_tts_model)
        return await websockets.connect(
            url,
            extra_headers={"Authorization": f"Token {settings.deepgram_api_key}"},
        )

    async def connect(self) -> None:
        self._ws = await self._open_ws()
        self._running = True
        asyncio.create_task(self._receive_loop())
        self._keepalive_task = asyncio.create_task(self._keepalive_loop())

    async def _keepalive_loop(self) -> None:
        while self._running and self._ws:
            try:
                await asyncio.sleep(self._KEEPALIVE_INTERVAL)
                if self._ws and self._running:
                    await self._ws.ping()
            except Exception:
                break

    def _start_background_reconnect(self) -> None:
        if self._reconnect_task is None or self._reconnect_task.done():
            self._reconnect_task = asyncio.create_task(self._reconnect())

    async def _reconnect(self) -> None:
        try:
            if self._ws:
                await self._ws.close()
        except Exception:
            pass
        try:
            self._ws = await self._open_ws()
            asyncio.create_task(self._receive_loop())
            self._keepalive_task = asyncio.create_task(self._keepalive_loop())
            logger.info("Deepgram TTS reconnected")
        except Exception as e:
            logger.error("Deepgram TTS reconnect failed: %s", e)
            self._running = False

    async def _ensure_connected(self) -> None:
        if self._reconnect_task is not None:
            await self._reconnect_task
            self._reconnect_task = None

    async def _receive_loop(self) -> None:
        if not self._ws:
            return
        try:
            async for message in self._ws:
                if isinstance(message, bytes):
                    await self._audio_queue.put(message)
                else:
                    data = json.loads(message)
                    if "error" in data:
                        logger.error("Deepgram TTS error: %s", data)
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Deepgram TTS connection closed")
            if self._running:
                self._start_background_reconnect()
        except Exception as e:
            logger.error("Deepgram TTS receive error: %s", e)
            if self._running:
                self._start_background_reconnect()

    async def send_text(self, text: str) -> None:
        await self._ensure_connected()
        if self._ws and self._running:
            msg = {"type": "Speak", "text": text}
            try:
                await self._ws.send(json.dumps(msg))
            except Exception as e:
                logger.error("Deepgram TTS send_text failed: %s", e)
                self._start_background_reconnect()

    async def flush(self) -> None:
        await self._ensure_connected()
        if self._ws and self._running:
            try:
                msg = {"type": "Flush"}
                await self._ws.send(json.dumps(msg))
            except Exception as e:
                logger.error("Deepgram TTS flush failed: %s", e)
                self._start_background_reconnect()

    async def interrupt(self) -> None:
        while not self._audio_queue.empty():
            try:
                self._audio_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        if self._ws and self._running:
            msg = {"type": "Clear"}
            try:
                await self._ws.send(json.dumps(msg))
            except Exception:
                pass

    async def get_audio(self) -> AsyncGenerator[bytes, None]:
        while True:
            if not self._running and self._audio_queue.empty():
                break
            try:
                audio = await asyncio.wait_for(self._audio_queue.get(), timeout=0.5)
                yield audio
            except asyncio.TimeoutError:
                continue

    async def close(self) -> None:
        self._running = False
        if self._keepalive_task:
            self._keepalive_task.cancel()
        if self._ws:
            try:
                msg = {"type": "Close"}
                await self._ws.send(json.dumps(msg))
            except Exception:
                pass
            await self._ws.close()


def _build_provider_pair() -> tuple[TTSProvider, TTSProvider]:
    primary_name = settings.tts_provider.lower()
    if primary_name == "elevenlabs":
        return ElevenLabsTTS(), DeepgramTTS()
    return DeepgramTTS(), ElevenLabsTTS()


class TTSWithFallback:
    def __init__(self) -> None:
        primary, fallback = _build_provider_pair()
        self._primary: TTSProvider = primary
        self._fallback: TTSProvider = fallback
        self._active: TTSProvider | None = None

    async def connect(self) -> None:
        try:
            await self._primary.connect()
            self._active = self._primary
        except Exception:
            logger.warning(
                "Primary TTS (%s) failed, falling back to %s",
                type(self._primary).__name__,
                type(self._fallback).__name__,
            )
            await self._fallback.connect()
            self._active = self._fallback

    async def send_text(self, text: str) -> None:
        if self._active:
            await self._active.send_text(text)

    async def flush(self) -> None:
        if self._active:
            await self._active.flush()

    async def interrupt(self) -> None:
        if self._active:
            await self._active.interrupt()

    async def get_audio(self) -> AsyncGenerator[bytes, None]:
        if self._active:
            async for chunk in self._active.get_audio():
                yield chunk

    async def close(self) -> None:
        if self._active:
            await self._active.close()
