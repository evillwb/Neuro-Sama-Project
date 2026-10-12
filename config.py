"""All the settings you are likely to want to change live here."""

# --- Character -------------------------------------------------------------
NAME = "Neuro"                     # Rename her to make her your own.
PERSONALITY_FILE = "personality.txt"

# --- Brain (Ollama, runs locally) -----------------------------------------
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:3b"       # Small and fast. Try "qwen2.5:7b" if your laptop is strong.
TEMPERATURE = 0.9                  # Higher = more chaotic.
MAX_HISTORY_MESSAGES = 20          # How many past messages she remembers.

# --- Ears (faster-whisper, runs locally) ----------------------------------
WHISPER_MODEL = "base.en"          # tiny.en (fastest) / base.en / small.en (most accurate)
WHISPER_DEVICE = "cpu"             # "cuda" if you have an NVIDIA GPU with CUDA set up
WHISPER_COMPUTE_TYPE = "int8"

MIC_DEVICE = None                  # None = default mic. Run `python main.py --devices` to list.
SILENCE_SECONDS = 0.8              # How long you must be quiet before she answers.
MIN_SPEECH_SECONDS = 0.3           # Ignore sounds shorter than this.
MAX_SPEECH_SECONDS = 30
MIC_SENSITIVITY = 3.0              # Lower = picks up quieter speech (and more noise).

# --- Voice (Piper, runs locally) ------------------------------------------
PIPER_VOICE = "voices/en_US-amy-medium.onnx"
VOICE_PITCH = 1.25                 # 1.0 = normal. Higher = cuter / more anime.
VOICE_SPEED = 1.0                  # 1.0 = normal. Higher = faster.
VOLUME = 1.0

SPEAKER_DEVICE = None              # None = default speakers. Run `python main.py --devices` to list.

# --- VTube Studio lip sync --------------------------------------------------
VTS_ENABLED = True
VTS_URL = "ws://localhost:8001"
VTS_MOUTH_PARAMETER = "MouthOpen"  # VTube Studio's default input parameter for the mouth.
VTS_MOUTH_GAIN = 6.0               # Raise if her mouth barely opens, lower if it's always wide open.
VTS_TOKEN_FILE = ".vts_token"
