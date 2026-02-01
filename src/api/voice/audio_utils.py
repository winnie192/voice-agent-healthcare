from __future__ import annotations

import audioop
import base64


def mulaw_to_pcm16(mulaw_bytes: bytes) -> bytes:
    return audioop.ulaw2lin(mulaw_bytes, 2)


def pcm16_to_mulaw(pcm_bytes: bytes) -> bytes:
    return audioop.lin2ulaw(pcm_bytes, 2)


def decode_twilio_media(payload: str) -> bytes:
    raw = base64.b64decode(payload)
    return mulaw_to_pcm16(raw)


def encode_for_twilio(pcm_bytes: bytes) -> str:
    mulaw = pcm16_to_mulaw(pcm_bytes)
    return base64.b64encode(mulaw).decode("ascii")
