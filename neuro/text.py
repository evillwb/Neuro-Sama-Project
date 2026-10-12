"""Helpers for turning streamed LLM text into clean, speakable sentences."""

import re

_SENTENCE_END = re.compile(r"(?<=[.!?…])[\"')\]]*\s+|\n+")
_ACTIONS = re.compile(r"\*[^*]*\*|\([^)]*\)|\[[^\]]*\]")
_NON_SPEECH = re.compile(r"[^\w\s.,!?'\"\-:;…]")
_SPACES = re.compile(r"\s+")


def clean_for_speech(text: str) -> str:
    """Remove things a TTS voice shouldn't read: *actions*, emojis, markdown."""
    text = _ACTIONS.sub(" ", text)
    text = _NON_SPEECH.sub(" ", text)
    return _SPACES.sub(" ", text).strip()


class SentenceSplitter:
    """Collects streamed tokens and hands back whole sentences as soon as they finish."""

    def __init__(self):
        self._buffer = ""

    def feed(self, token: str) -> list[str]:
        self._buffer += token
        parts = _SENTENCE_END.split(self._buffer)
        self._buffer = parts.pop()
        return [s for s in (clean_for_speech(p) for p in parts) if s]

    def flush(self) -> list[str]:
        rest, self._buffer = clean_for_speech(self._buffer), ""
        return [rest] if rest else []
