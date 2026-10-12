"""The brain: a local LLM served by Ollama, plus short-term memory."""

import json
from pathlib import Path
from typing import Iterator

import requests

import config


class Brain:
    def __init__(self):
        personality = Path(config.PERSONALITY_FILE).read_text(encoding="utf-8")
        self.system_prompt = personality.replace("{name}", config.NAME)
        self.history: list[dict] = []

    def check(self):
        """Fail early with a helpful message if Ollama isn't running or the model is missing."""
        try:
            tags = requests.get(f"{config.OLLAMA_URL}/api/tags", timeout=5).json()
        except requests.RequestException:
            raise SystemExit(
                f"Can't reach Ollama at {config.OLLAMA_URL}. Is the Ollama app running?"
            )
        names = {m["name"] for m in tags.get("models", [])}
        if config.OLLAMA_MODEL not in names and f"{config.OLLAMA_MODEL}:latest" not in names:
            raise SystemExit(
                f"Model '{config.OLLAMA_MODEL}' isn't downloaded. "
                f"Run: ollama pull {config.OLLAMA_MODEL}"
            )

    def reply(self, user_text: str) -> Iterator[str]:
        """Stream her reply token by token, and remember the exchange."""
        self.history.append({"role": "user", "content": user_text})
        self.history = self.history[-config.MAX_HISTORY_MESSAGES:]
        messages = [{"role": "system", "content": self.system_prompt}, *self.history]

        response = requests.post(
            f"{config.OLLAMA_URL}/api/chat",
            json={
                "model": config.OLLAMA_MODEL,
                "messages": messages,
                "stream": True,
                "options": {"temperature": config.TEMPERATURE},
            },
            stream=True,
            timeout=120,
        )
        response.raise_for_status()

        full = ""
        for line in response.iter_lines():
            if not line:
                continue
            chunk = json.loads(line)
            token = chunk.get("message", {}).get("content", "")
            full += token
            yield token
            if chunk.get("done"):
                break

        self.history.append({"role": "assistant", "content": full.strip()})
