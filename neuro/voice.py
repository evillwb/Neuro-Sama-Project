"""The voice: Piper text-to-speech, played on the speakers while moving her mouth in VTube Studio.

Sentences are spoken as soon as the brain finishes them, so she starts talking before
the whole reply is written. One thread makes audio, another plays it.
"""

import queue
import threading
from pathlib import Path

import numpy as np
import sounddevice as sd
from piper import PiperVoice, SynthesisConfig

import config
from neuro.vts import VTubeStudio

PLAY_BLOCK_SECONDS = 0.05


def change_pitch(audio: np.ndarray, rate: int, pitch: float, out_rate: int) -> np.ndarray:
    """Resample so the audio plays `pitch` times higher at `out_rate`.

    Speeding audio up raises its pitch but also makes it shorter; we make Piper speak
    slower by the same amount (see length_scale below) so the speed stays natural.
    """
    out_len = int(len(audio) * out_rate / (rate * pitch))
    positions = np.linspace(0, len(audio) - 1, out_len)
    return np.interp(positions, np.arange(len(audio)), audio).astype(np.float32)


class Voice:
    def __init__(self, vts: VTubeStudio | None = None):
        model = Path(config.PIPER_VOICE)
        if not model.exists():
            raise SystemExit(
                f"Voice file {model} not found. Download one with:\n"
                f"  python -m piper.download_voices --download-dir voices {model.stem}"
            )
        print(f"Loading voice '{model.stem}'...")
        self.piper = PiperVoice.load(model)
        self.synth_config = SynthesisConfig(
            length_scale=config.VOICE_PITCH / config.VOICE_SPEED,
            volume=config.VOLUME,
        )
        self.out_rate = int(
            sd.query_devices(config.SPEAKER_DEVICE, "output")["default_samplerate"]
        )
        self.vts = vts

        self._sentences: queue.Queue = queue.Queue()
        self._audio: queue.Queue = queue.Queue()
        threading.Thread(target=self._synth_loop, daemon=True).start()
        threading.Thread(target=self._play_loop, daemon=True).start()

    def say(self, sentence: str):
        """Queue a sentence to be spoken. Returns immediately."""
        self._sentences.put(sentence)

    def wait(self):
        """Block until everything queued has been spoken."""
        self._sentences.join()
        self._audio.join()

    def _synth_loop(self):
        while True:
            sentence = self._sentences.get()
            try:
                for chunk in self.piper.synthesize(sentence, self.synth_config):
                    self._audio.put(change_pitch(
                        chunk.audio_float_array, chunk.sample_rate,
                        config.VOICE_PITCH, self.out_rate,
                    ))
            except Exception as e:
                print(f"[voice error] {e}")
            finally:
                self._sentences.task_done()

    def _play_loop(self):
        block = int(self.out_rate * PLAY_BLOCK_SECONDS)
        mouth = 0.0
        with sd.OutputStream(
            samplerate=self.out_rate, channels=1, dtype="float32",
            device=config.SPEAKER_DEVICE,
        ) as stream:
            while True:
                audio = self._audio.get()
                try:
                    for start in range(0, len(audio), block):
                        piece = audio[start:start + block]
                        if self.vts:
                            loudness = float(np.sqrt(np.mean(piece**2))) * config.VTS_MOUTH_GAIN
                            mouth = 0.5 * mouth + 0.5 * min(loudness, 1.0)  # smooth flapping
                            self.vts.set_mouth(mouth)
                        stream.write(piece.reshape(-1, 1))
                finally:
                    if self.vts and self._audio.qsize() == 0:
                        mouth = 0.0
                        self.vts.set_mouth(0.0)
                    self._audio.task_done()
