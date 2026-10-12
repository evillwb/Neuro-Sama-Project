# Neuro-Sama-Project

A local AI VTuber you talk to through your mic. Everything runs on your own laptop, for free.

```
Your mic ──► Whisper (hears you) ──► Ollama (thinks) ──► Piper (speaks) ──► Speakers
                                                                    └──► VTube Studio (mouth moves)
```

## Setup (one time)

1. **Install Python 3.10 or newer** from https://www.python.org/downloads/.
   On Windows, tick **"Add Python to PATH"** in the installer.

2. **Install Ollama** (runs the AI brain) from https://ollama.com/download, then open a terminal and download a model:
   ```
   ollama pull llama3.2:3b
   ```

3. **Install this project.** In a terminal, inside this folder:
   ```
   python -m venv .venv
   .venv\Scripts\activate          # Windows
   source .venv/bin/activate       # Mac / Linux
   pip install -r requirements.txt
   ```

4. **Download her voice:**
   ```
   python -m piper.download_voices --download-dir voices en_US-amy-medium
   ```
   Browse other voices at https://rhasspy.github.io/piper-samples/, then change `PIPER_VOICE` in `config.py`.

5. **Turn on the VTube Studio API:** open VTube Studio, go to **Settings**, scroll down and turn on **Start API** (port 8001).

## Run it

Open VTube Studio with your avatar loaded, make sure Ollama is running, then:

```
.venv\Scripts\activate
python main.py
```

The first time, VTube Studio shows a popup asking to allow the plugin. Click **Allow**.

Stay quiet for a second while it calibrates the mic. After that, just talk. She answers when you stop speaking.

Other ways to run it:

| Command | What it does |
|---|---|
| `python main.py --text` | Type instead of talking. Good for testing. |
| `python main.py --no-vts` | Run without VTube Studio. |
| `python main.py --devices` | List your mics and speakers, so you can pick one in `config.py`. |

**Use headphones.** She stops listening while she talks, but with speakers your mic may still pick up the end of her sentences.

## Make her your own

- **Personality:** edit `personality.txt`.
- **Name, voice pitch, speed, AI model, mic sensitivity:** edit `config.py`.

## Troubleshooting

| Problem | Fix |
|---|---|
| "Can't reach Ollama" | Start the Ollama app. |
| She doesn't hear you | Lower `MIC_SENSITIVITY`, or set `MIC_DEVICE` (see `--devices`). |
| She answers background noise | Raise `MIC_SENSITIVITY`. |
| Replies are slow | Use a smaller model (`llama3.2:1b`) or `WHISPER_MODEL = "tiny.en"`. |
| Mouth barely moves / always open | Raise or lower `VTS_MOUTH_GAIN`. |
| Mouth doesn't move at all | In VTube Studio's model settings, check the **MouthOpen** input is linked to your model's mouth parameter. |
| Wrong mic or speakers | Set `MIC_DEVICE` / `SPEAKER_DEVICE` to a number from `--devices`. |
