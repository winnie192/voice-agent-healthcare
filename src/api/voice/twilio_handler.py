from __future__ import annotations

import asyncio
import base64
import json
from typing import TYPE_CHECKING

from src.api.agents.orchestrator import BusinessContext, CallSession, process_utterance
from src.api.voice.audio_utils import decode_twilio_media
from src.api.voice.stt import DeepgramSTT
from src.api.voice.tts import TTSWithFallback

if TYPE_CHECKING:
    import websockets
    from sqlalchemy.ext.asyncio import AsyncSession


class TwilioCallHandler:
    def __init__(
        self,
        twilio_ws: websockets.WebSocketServerProtocol,
        business_context: BusinessContext,
        db_session: AsyncSession,
    ) -> None:
        self._twilio_ws = twilio_ws
        self._stt = DeepgramSTT()
        self._tts = TTSWithFallback()
        self._call_session = CallSession(business=business_context, session=db_session)
        self._stream_sid: str | None = None
        self._is_speaking = False
        self._current_response_task: asyncio.Task | None = None

    async def handle(self) -> None:
        await self._stt.connect()
        await self._tts.connect()

        greeting = (
            f"Hi, thanks for calling {self._call_session.business.name}. "
            "How can I help you?"
        )
        await self._tts.send_text(greeting)
        await self._tts.flush()
        self._call_session.conversation_history.append(
            {"role": "agent", "content": greeting}
        )

        transcription_task = asyncio.create_task(self._process_transcriptions())
        tts_playback_task = asyncio.create_task(self._stream_tts_to_twilio())
        bargein_task = asyncio.create_task(self._monitor_bargein())

        try:
            async for message in self._twilio_ws:
                data = json.loads(message)
                event = data.get("event")

                if event == "start":
                    self._stream_sid = data["start"]["streamSid"]
                elif event == "media":
                    payload = data["media"]["payload"]
                    pcm = decode_twilio_media(payload)
                    await self._stt.send_audio(pcm)
                elif event == "stop":
                    break
        finally:
            await self._stt.close()
            await self._tts.close()
            transcription_task.cancel()
            tts_playback_task.cancel()
            bargein_task.cancel()

    async def _handle_bargein(self) -> None:
        if self._current_response_task and not self._current_response_task.done():
            self._current_response_task.cancel()

        await self._tts.interrupt()

        if self._stream_sid:
            clear_msg = {
                "event": "clear",
                "streamSid": self._stream_sid,
            }
            await self._twilio_ws.send(json.dumps(clear_msg))

        self._is_speaking = False

    async def _monitor_bargein(self) -> None:
        while True:
            await self._stt.wait_for_speech()
            if self._is_speaking:
                await self._handle_bargein()
            self._stt.clear_speech_flag()

    async def _process_transcriptions(self) -> None:
        async for transcript in self._stt.get_transcripts():
            self._current_response_task = asyncio.create_task(
                self._generate_and_speak(transcript)
            )
            await self._current_response_task

    async def _generate_and_speak(self, transcript: str) -> None:
        self._is_speaking = True
        try:
            async for text_chunk in process_utterance(self._call_session, transcript):
                await self._tts.send_text(text_chunk)
            await self._tts.flush()
        except asyncio.CancelledError:
            pass
        finally:
            self._is_speaking = False

    async def _stream_tts_to_twilio(self) -> None:
        async for audio_chunk in self._tts.get_audio():
            if self._stream_sid:
                payload = base64.b64encode(audio_chunk).decode("ascii")
                msg = {
                    "event": "media",
                    "streamSid": self._stream_sid,
                    "media": {"payload": payload},
                }
                await self._twilio_ws.send(json.dumps(msg))
