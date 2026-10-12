"""The ears: listen on the mic until you stop talking, then transcribe with Whisper."""

import collections
import queue

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

import config

SAMPLE_RATE = 16000
BLOCK_SECONDS = 0.03
BLOCK = int(SAMPLE_RATE * BLOCK_SECONDS)


def _rms(block: np.ndarray) -> float:
    return float(np.sqrt(np.mean(block**2)))


class Ears:
    def __init__(self):
        print(f"Loading Whisper '{config.WHISPER_MODEL}'...")
        self.model = WhisperModel(
            config.WHISPER_MODEL,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE_TYPE,
        )
        self.threshold = None

    def _open_stream(self, blocks: queue.Queue):
        def callback(indata, frames, time, status):
            blocks.put(indata[:, 0].copy())

        return sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=BLOCK,
            device=config.MIC_DEVICE,
            callback=callback,
        )

    def calibrate(self, seconds: float = 1.5):
        """Measure background noise so we know how loud 'talking' is."""
        print("Calibrating mic, stay quiet for a moment...")
        blocks: queue.Queue = queue.Queue()
        with self._open_stream(blocks):
            levels = [_rms(blocks.get()) for _ in range(int(seconds / BLOCK_SECONDS))]
        noise = float(np.percentile(levels, 90))
        self.threshold = max(noise * config.MIC_SENSITIVITY, 0.005)

    def listen(self) -> np.ndarray:
        """Block until one phrase has been spoken, and return its audio."""
        if self.threshold is None:
            self.calibrate()

        silence_blocks = int(config.SILENCE_SECONDS / BLOCK_SECONDS)
        max_blocks = int(config.MAX_SPEECH_SECONDS / BLOCK_SECONDS)
        min_blocks = int(config.MIN_SPEECH_SECONDS / BLOCK_SECONDS)
        preroll = collections.deque(maxlen=int(0.3 / BLOCK_SECONDS))

        blocks: queue.Queue = queue.Queue()
        with self._open_stream(blocks):
            while True:
                speech: list[np.ndarray] = []
                loud = quiet = 0
                while True:
                    block = blocks.get()
                    is_loud = _rms(block) > self.threshold
                    if not speech:
                        preroll.append(block)
                        if is_loud:
                            speech = list(preroll)
                            loud = 1
                        continue
                    speech.append(block)
                    loud += is_loud
                    quiet = 0 if is_loud else quiet + 1
                    if quiet >= silence_blocks or len(speech) >= max_blocks:
                        break
                if loud >= min_blocks:
                    return np.concatenate(speech)
                preroll.clear()

    def transcribe(self, audio: np.ndarray) -> str:
        segments, _ = self.model.transcribe(
            audio, language="en", beam_size=1, vad_filter=True
        )
        return " ".join(s.text.strip() for s in segments).strip()
