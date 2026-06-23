---
title: Healthcare Translation
emoji: 🩺
colorFrom: yellow
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# Healthcare-Translation Web App

A web-based prototype that enables real-time, multilingual translation between patients and healthcare providers, with a **pronunciation-intelligence layer** built specifically for medical terminology. The app turns speech into text, scores how confident the recognizer was about each word, flags risky medical terms for review, learns from human corrections, and shows clinicians how to correctly pronounce drug names and medical conditions (IPA + a plain-English guide).

## Features

- **Voice-to-Text**: Records audio in the browser (`MediaRecorder`) and transcribes it with `faster-whisper`, run locally. Auto-stops after a stretch of silence.
- **Real-Time Translation**: Translates clinical text with local Helsinki-NLP (Opus-MT) transformer models — no external translation API required.
- **Medical Pronunciation Layer (G2P)**: Detects medical terms and annotates them with IPA, a simplified readable guide (e.g. `ay-TOR-va-STA-tin`), syllable breakdown, and stress pattern. Hover any underlined term for a tooltip with a "Hear it" button. A 90-term curated dictionary takes priority over an automatic grapheme-to-phoneme fallback.
- **Per-Word Confidence Scoring**: Extracts word-level probabilities from `faster-whisper` and flags uncertain words (amber) and high-risk medical terms (red), with an overall confidence badge.
- **Human-in-the-Loop Corrections**: Click any flagged word to correct it. Corrections are stored in SQLite, re-applied to future transcripts, counted on a header badge, and exportable as CSV for later model fine-tuning.
- **Out-of-Vocabulary (OOV) Detection**: Flags words the recognizer likely struggles with — combining low confidence, absence from a common-word list, and drug-suffix patterns (`-statin`, `-mab`, `-pril`, …) — and logs them in a dedicated panel.
- **Audio Playback**: Speaks the translated text using the Web Speech API.
- **Translation History**: Saves and displays past translations.
- **Responsive Design**: Works down to 375px wide; respects `prefers-reduced-motion`.

## Design
The UI uses the **"Mesa" editorial-dark theme** in a yellowish-blue palette — a warm amber-yellow accent and deep navy on a blue-tinted near-black ground, with the Fraunces / Inter / Roboto Mono font stack. The signature element is a **real-time waveform visualizer** that animates in amber while recording. All design tokens live in `app/static/css/tokens.css`; no colors are hardcoded in component CSS.

## Technologies Used

- **Framework**: Flask (backend & server-rendered frontend)
- **Speech Recognition**: `faster-whisper` (local Whisper model, word-level timestamps + probabilities)
- **Translation**: Helsinki-NLP Opus-MT models via `transformers` + `PyTorch` (local)
- **Pronunciation**: curated 90-term medical dictionary with `g2p-en` as a fallback G2P engine
- **Feedback store**: SQLite (`data/corrections.db`)
- **Security**: Flask-Talisman
- **UI**: HTML, CSS, JavaScript (Web Audio API for the waveform)
- **Deployment**: Docker → Hugging Face Spaces (also Render-ready)

## API

All endpoints return a `{ success, data, error }` envelope where noted.

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/transcribe` | Speech-to-text; returns per-word confidence + OOV terms |
| `POST` | `/api/translate` | Translate text; returns IPA-annotated output |
| `POST` | `/api/pronunciation/annotate` | Annotate text with IPA pronunciation |
| `GET`  | `/api/pronunciation/term?term=` | Pronunciation for a single term |
| `POST` | `/api/feedback/correction` | Store a human correction |
| `GET`  | `/api/feedback/corrections` | List all stored corrections |
| `GET`  | `/api/feedback/corrections/export` | Download corrections as CSV |
| `GET`  | `/api/oov/log` | Out-of-vocabulary terms flagged this session |
| `GET`  | `/api/oov/stats` | OOV counts by category |
| `GET`  | `/api/health` | Health check |

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/anjolakabiawu/Healthcare-Translation.git
   cd Healthcare-Translation
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   # Windows:  .venv\Scripts\activate
   # macOS/Linux:  source .venv/bin/activate
   pip install -r requirements.txt
   ```

   > The pronunciation layer's `g2p-en` engine downloads a small NLTK data set
   > (`averaged_perceptron_tagger`, `cmudict`) on first use. If it is unavailable,
   > `g2p_medical` falls back to a heuristic so the app keeps working.

3. Configure environment variables (see `.env.example`):
   ```bash
   cp .env.example .env
   ```

4. Run the app:
   ```bash
   python run.py
   ```
   Then open http://localhost:5000.

## Deployment (Hugging Face Spaces)

The app is deployed as a **Docker Space** on Hugging Face. The model stack
(PyTorch + Whisper + Helsinki-NLP) needs ~1–3 GB RAM, which exceeds typical
free serverless limits — HF Spaces' free CPU tier (16 GB RAM) handles it well.

### How it's configured

- The YAML block at the top of this README is the Space config — `sdk: docker`
  and `app_port: 7860` (HF routes traffic to 7860).
- The `Dockerfile` installs `ffmpeg` (so `faster-whisper` can decode WebM/OGG
  audio), runs as a non-root user (HF runs containers as UID 1000), and starts
  gunicorn bound to `$PORT`.
- `ProductionConfig` defaults the Whisper model to `tiny` to keep memory/cost
  down; override with the `WHISPER_MODEL_SIZE` env var (`tiny|base|small|medium`).

### First-time setup

1. Create a Space at <https://huggingface.co/new-space> → SDK **Docker** →
   hardware **CPU basic (free)**.
2. Create a **write token** at <https://huggingface.co/settings/tokens>.
3. Add the Space as a git remote and push:
   ```bash
   git remote add space https://huggingface.co/spaces/<username>/<space-name>
   git push space main          # username = HF username, password = write token
   ```

### Notes / gotchas

- **No binary files in git history.** HF rejects committed binaries — store them
  in Git LFS, or keep them out of the repo. (This project uses an inline SVG
  favicon to avoid the issue entirely.)
- Add a `requirements.txt` so the build resolves all deps — don't rely on
  transitive ones (e.g. `requests`).
- **Faster downloads:** add an `HF_TOKEN` secret in the Space settings to lift
  model-download rate limits and speed up cold starts.
- After each push, the Space rebuilds automatically; watch the **Logs** tab. The
  first transcription downloads the model weights (~30–60s, one-time per boot).

> Also Render-ready: a `render.yaml` blueprint is included (deploys the same
> Dockerfile; bump `plan: free` → `starter` for enough RAM).

## Project Structure

```text
app/
├── __init__.py              # app factory + blueprint registration
├── routes/                  # transcribe, translate, pronunciation, feedback, oov, history, languages
├── services/                # transcription, translation, glossary
├── pronunciation/           # g2p_medical, ipa_display, confidence, oov_detector
├── feedback/                # correction_store (SQLite)
├── static/css/              # tokens.css + styles.css (Mesa theme)
├── static/js/               # waveform, nav, pronunciation, feedback, app
└── templates/index.html
data/
├── medical_dictionary.py    # 90-term curated pronunciation dictionary
├── glossary.csv             # term highlighting + translations (EN→ES, EN→FR)
└── corrections.db           # SQLite feedback store (created at runtime)
run.py                       # entry point
```

## Testing

```bash
pytest                                       # full suite
python -m app.pronunciation.g2p_medical      # module self-check
python -m app.pronunciation.ipa_display      # module self-check
python -m app.pronunciation.confidence       # module self-check
python -m app.pronunciation.oov_detector     # module self-check
python -m app.feedback.correction_store      # module self-check
```
