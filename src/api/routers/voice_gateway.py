from __future__ import annotations

import asyncio
import audioop
import base64
import json
import logging
import time

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from twilio.twiml.voice_response import Connect, Stream, VoiceResponse

from src.api.agents.orchestrator import (
    BusinessContext,
    CallSession,
    pick_filler_phrase,
    process_utterance,
)
from src.api.db.engine import get_session
from src.api.db.queries import get_business_by_phone
from src.api.voice.stt import DeepgramSTT
from src.api.voice.tts import TTSWithFallback
from src.api.voice.twilio_handler import TwilioCallHandler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["voice"])

ECHO_SUPPRESSION_SECONDS = 0.5
FIRST_CHUNK_SIZE = 50
SUBSEQUENT_CHUNK_SIZE = 80


@router.post("/twilio/incoming")
async def twilio_incoming(request: Request) -> Response:
    form = await request.form()
    to_number = str(form.get("To", ""))

    response = VoiceResponse()
    connect = Connect()
    host = request.headers.get("host", "localhost")
    stream = Stream(url=f"wss://{host}/voice/ws/{to_number}")
    connect.append(stream)
    response.append(connect)

    return Response(content=str(response), media_type="application/xml")


@router.websocket("/ws/{business_phone}")
async def voice_websocket(
    websocket: WebSocket,
    business_phone: str,
) -> None:
    await websocket.accept()

    async for session in get_session():
        business = await get_business_by_phone(session, business_phone)
        if not business:
            await websocket.close(code=1008, reason="Business not found")
            return

        context = BusinessContext(
            business_id=business.id,
            name=business.name,
            location=business.location or "",
            hours=str(business.hours) if business.hours else "",
            policies=business.policies or "",
        )

        handler = TwilioCallHandler(
            twilio_ws=websocket,
            business_context=context,
            db_session=session,
        )
        await handler.handle()
        break


@router.websocket("/browser-ws/{business_phone}")
async def browser_voice_websocket(
    websocket: WebSocket,
    business_phone: str,
) -> None:
    await websocket.accept()

    try:
        async for session in get_session():
            business = await get_business_by_phone(session, business_phone)
            if not business:
                await websocket.close(code=1008, reason="Business not found")
                return

            context = BusinessContext(
                business_id=business.id,
                name=business.name,
                location=business.location or "",
                hours=str(business.hours) if business.hours else "",
                policies=business.policies or "",
            )

            client_sample_rate = 48000
            try:
                raw = await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
                data = json.loads(raw)
                if data.get("event") == "config":
                    client_sample_rate = int(data.get("sampleRate", 48000))
            except asyncio.TimeoutError:
                pass

            deepgram_rate = 16000
            resample_state = None
            stt = DeepgramSTT()
            tts = TTSWithFallback()
            call_session = CallSession(business=context, session=session)
            is_speaking = False
            current_response_task: asyncio.Task | None = None

            try:
                await stt.connect(sample_rate=deepgram_rate)
            except Exception as e:
                logger.error("Failed to connect Deepgram STT: %s", e)
                await websocket.close(code=1011, reason="STT connection failed")
                return

            try:
                await tts.connect()
            except Exception as e:
                logger.error("Failed to connect ElevenLabs TTS: %s", e)
                await stt.close()
                await websocket.close(code=1011, reason="TTS connection failed")
                return

            greeting = f"Hi, thanks for calling {context.name}. How can I help you?"
            await tts.send_text(greeting)
            await tts.flush()
            call_session.conversation_history.append(
                {"role": "agent", "content": greeting}
            )

            async def process_transcriptions() -> None:
                nonlocal is_speaking, current_response_task
                async for transcript in stt.get_transcripts():
                    if is_speaking:
                        continue

                    is_speaking = True
                    try:
                        filler = pick_filler_phrase(transcript)
                        if filler:
                            await tts.send_text(filler)
                            await tts.flush()

                        delay_filler_task: asyncio.Task[None] | None = None

                        async def _send_delay_filler() -> None:
                            await asyncio.sleep(4.0)
                            await tts.send_text("Still looking, one moment...")

                        delay_filler_task = asyncio.create_task(_send_delay_filler())

                        text_buffer = ""
                        first_chunk = True
                        async for text_chunk in process_utterance(
                            call_session, transcript
                        ):
                            if delay_filler_task and not delay_filler_task.done():
                                delay_filler_task.cancel()
                                delay_filler_task = None
                            text_buffer += text_chunk
                            threshold = (
                                FIRST_CHUNK_SIZE
                                if first_chunk
                                else SUBSEQUENT_CHUNK_SIZE
                            )
                            if len(text_buffer) >= threshold or any(
                                text_buffer.rstrip().endswith(p) for p in ".!?,"
                            ):
                                await tts.send_text(text_buffer)
                                text_buffer = ""
                                first_chunk = False
                        if text_buffer:
                            await tts.send_text(text_buffer)
                        await tts.flush()
                    except asyncio.CancelledError:
                        pass
                    except Exception as e:
                        logger.error("Error in process_transcriptions: %s", e)
                        try:
                            fallback = (
                                "Sorry, I had trouble with that. "
                                "Could you say that again?"
                            )
                            await tts.send_text(fallback)
                            await tts.flush()
                        except Exception:
                            pass
                    finally:
                        if delay_filler_task and not delay_filler_task.done():
                            delay_filler_task.cancel()
                        is_speaking = False
                        while not stt._transcript_queue.empty():
                            stt._transcript_queue.get_nowait()

            last_tts_send_time = 0.0

            async def stream_tts_to_client() -> None:
                nonlocal last_tts_send_time
                async for audio_chunk in tts.get_audio():
                    payload = base64.b64encode(audio_chunk).decode("ascii")
                    try:
                        await websocket.send_json(
                            {
                                "event": "media",
                                "media": {"payload": payload},
                            }
                        )
                        last_tts_send_time = time.monotonic()
                    except WebSocketDisconnect:
                        break

            transcription_task = asyncio.create_task(process_transcriptions())
            tts_playback_task = asyncio.create_task(stream_tts_to_client())

            try:
                while True:
                    raw = await websocket.receive_text()
                    data = json.loads(raw)
                    event = data.get("event")

                    if event == "media":
                        payload = data["media"]["payload"]
                        pcm = base64.b64decode(payload)

                        if (
                            time.monotonic() - last_tts_send_time
                            < ECHO_SUPPRESSION_SECONDS
                        ):
                            continue

                        if client_sample_rate != deepgram_rate:
                            pcm_resampled, resample_state = audioop.ratecv(
                                pcm,
                                2,
                                1,
                                client_sample_rate,
                                deepgram_rate,
                                resample_state,
                            )
                        else:
                            pcm_resampled = pcm

                        await stt.send_audio(pcm_resampled)
                    elif event == "stop":
                        break
            except WebSocketDisconnect:
                pass
            except Exception as e:
                logger.error("Error in browser voice loop: %s", e)
            finally:
                await stt.close()
                await tts.close()
                transcription_task.cancel()
                tts_playback_task.cancel()

            break
    except Exception:
        logger.exception("Browser voice websocket error")
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
