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

A web-based prototype that enables real-time, multilingual translation between patients and healthcare providers. The app converts spoken input into text, provides a live transcript, offers a translated version with audio playback, and adds a pronunciation-intelligence layer that helps clinicians say medical terms correctly.

## Features
- **Voice-to-Text**: Converts spoken input into text using `faster-whisper`, run locally.
- **Real-Time Translation**: Translates clinical text with local Helsinki-NLP (Opus-MT) transformer models — no external translation API required.
- **Medical Pronunciation Layer**: Detects medical terms in the text and annotates them with IPA, a simplified readable guide (e.g. `ay-TOR-va-STA-tin`), syllable breakdown, and stress pattern. Hover any underlined term for a tooltip with a "Hear it" button.
- **Audio Playback**: Speaks the translated text using the Web Speech API.
- **Translation History**: Saves and displays past translations.
- **Responsive Design**: Works down to 375px wide; respects `prefers-reduced-motion`.

## Design
The UI uses the **"Mesa" editorial-dark theme** in a yellowish-blue palette — a warm amber-yellow accent and deep navy on a blue-tinted near-black ground, with the Fraunces / Inter / Roboto Mono font stack. The signature element is a **real-time waveform visualizer** that animates in amber while recording. All design tokens live in `app/static/css/tokens.css`; no colors are hardcoded in component CSS.

## Technologies Used
- **Framework**: Flask (backend & server-rendered frontend)
- **Speech Recognition**: `faster-whisper` (local Whisper model)
- **Translation**: Helsinki-NLP Opus-MT models via `transformers` + `PyTorch` (local)
- **Pronunciation**: curated medical dictionary (74 terms) with `g2p-en` as a fallback G2P engine
- **Security**: Flask-Talisman
- **UI**: HTML, CSS, JavaScript (Web Audio API for the waveform)
- **Deployment**: Render / Docker

## API
All endpoints return a `{ success, data, error }` envelope where noted.

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/transcribe` | Speech-to-text from raw audio |
| `POST` | `/api/translate` | Translate text; returns annotated output |
| `POST` | `/api/pronunciation/annotate` | Annotate text with IPA pronunciation |
| `GET`  | `/api/pronunciation/term?term=` | Pronunciation for a single term |
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

## Project Structure

```text
app/
├── __init__.py              # app factory + blueprint registration
├── routes/                  # transcribe, translate, pronunciation, history, languages
├── services/                # transcription, translation, glossary
├── pronunciation/           # g2p_medical, ipa_display  (Features 1 & 2)
├── static/css/              # tokens.css + styles.css (Mesa theme)
├── static/js/               # waveform, nav, pronunciation, app
└── templates/index.html
data/
└── medical_dictionary.py    # 74-term curated pronunciation dictionary
run.py                       # entry point
```

## Testing

```bash
pytest                       # full suite
python -m app.pronunciation.g2p_medical   # module self-check
python -m app.pronunciation.ipa_display   # module self-check
```
