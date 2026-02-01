from __future__ import annotations

import json

from src.api.voice.stt import DeepgramSTT


def _make_result(transcript: str, is_final: bool, speech_final: bool = False) -> str:
    return json.dumps(
        {
            "type": "Results",
            "is_final": is_final,
            "speech_final": speech_final,
            "channel": {"alternatives": [{"transcript": transcript}]},
        }
    )


def _make_utterance_end() -> str:
    return json.dumps({"type": "UtteranceEnd"})


class TestDeepgramSTTTurnDetection:
    def test_emits_transcript_on_speech_final(self) -> None:
        stt = DeepgramSTT()

        msg1 = json.loads(_make_result("I want to", is_final=True))
        msg2 = json.loads(
            _make_result("book a dental cleaning", is_final=True, speech_final=True)
        )

        transcript1 = msg1["channel"]["alternatives"][0]["transcript"]
        stt._utterance_buffer.append(transcript1.strip())

        transcript2 = msg2["channel"]["alternatives"][0]["transcript"]
        stt._utterance_buffer.append(transcript2.strip())
        stt._flush_utterance_buffer()

        result = stt._transcript_queue.get_nowait()
        assert result == "I want to book a dental cleaning"

    def test_emits_transcript_on_utterance_end(self) -> None:
        stt = DeepgramSTT()

        stt._utterance_buffer.append("hello there")
        stt._utterance_buffer.append("how are you")
        stt._flush_utterance_buffer()

        result = stt._transcript_queue.get_nowait()
        assert result == "hello there how are you"

    def test_does_not_emit_on_is_final_alone(self) -> None:
        stt = DeepgramSTT()

        stt._utterance_buffer.append("I want to")

        assert stt._transcript_queue.empty()

    def test_flush_clears_buffer(self) -> None:
        stt = DeepgramSTT()

        stt._utterance_buffer.append("hello")
        stt._flush_utterance_buffer()

        assert stt._utterance_buffer == []
        assert not stt._transcript_queue.empty()

    def test_flush_empty_buffer_is_noop(self) -> None:
        stt = DeepgramSTT()

        stt._flush_utterance_buffer()

        assert stt._transcript_queue.empty()
