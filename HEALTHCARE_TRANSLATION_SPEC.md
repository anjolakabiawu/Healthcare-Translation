# Healthcare Translation App — Rebuild Spec
**For Claude Code execution**

---

## Project Overview

This is a rebuild and feature expansion of an existing healthcare translation web app. The current app uses faster-whisper for speech-to-text and Helsinki-NLP transformer models for medical phrase translation. The goal is to add pronunciation intelligence features that make it genuinely useful for medical professionals, and to redesign the UI to be visually distinctive and production-quality.

---

## Current State

- Backend: Flask (Python)
- STT: faster-whisper (local Whisper model)
- Translation: Helsinki-NLP local transformer models (replaced DeepL)
- Frontend: HTML, CSS, JavaScript
- Deployment: Render or similar

Read all existing files carefully before touching anything. Understand the current architecture fully before making changes.

---

## Design System

### Theme Reference
Read the existing portfolio project folder at the path the user provides. Extract:
- All CSS custom properties (color tokens, spacing, border-radius, font stacks)
- Typography: font families, weights, sizes used
- Component patterns: card styles, button styles, input styles, nav styles
- Animation and transition patterns

### Color Direction
The new theme should use a **yellowish-blue** palette. Interpret this as:
- **Primary accent**: warm amber-yellow (approximately #E8B84B or similar golden tone)
- **Secondary accent**: deep blue (approximately #1A3A6B or a rich navy)
- **Background**: very dark near-black with a slight blue tint (approximately #080E1A)
- **Surface**: dark card background (approximately #0F1829)
- **Text primary**: warm off-white (#F0EDE6)
- **Text secondary**: muted gray-blue (#8A9BB5)
- **Success state**: soft teal (#2DD4BF)
- **Warning/flag state**: amber (#F59E0B)
- **Error state**: muted red (#EF4444)

Adjust these exact values if reading the portfolio folder gives you a better calibration. The portfolio's structural tokens (spacing, border-radius, font stack) should be preserved and extended. The color direction above is the new intent.

### Typography
- Keep whatever display/serif face is used in the portfolio for headings
- Body and UI: clean sans-serif (Inter, DM Sans, or what the portfolio uses)
- Monospace: for IPA phonetic output, confidence scores, and technical data display

### Signature Design Element
The single memorable element for this app: **a waveform visualizer that animates in real time while the user is speaking**, rendered in the amber-yellow accent color against the dark background. This sits at the center of the recording interface and is the emotional core of the experience.

---

## Features to Build

Build all five features as separate, well-structured Python modules in the backend. Each should be independently importable and testable.

---

### Feature 1: Medical Term G2P Pronunciation Layer

**Module**: `pronunciation/g2p_medical.py`

**What it does**: Converts written medical terms to their correct phonetic representation using grapheme-to-phoneme modeling, with a custom dictionary layer for medical terminology that standard G2P gets wrong.

**Implementation**:
- Install `g2p-en` as the base G2P engine
- Build a `MedicalG2P` class that first checks a custom medical dictionary before falling back to g2p-en
- The custom dictionary should include at minimum 50 common medical terms with their correct IPA and simplified pronunciation guide
- Terms to include: drug names (Atorvastatin, Metformin, Lisinopril, Omeprazole, Azithromycin, Hydrochlorothiazide), anatomical terms (Pharynx, Larynx, Trachea, Diaphragm, Femur, Patella, Clavicle), conditions (Myocardial, Pneumonia, Hypertension, Hyperlipidemia, Osteoporosis, Psoriasis, Fibromyalgia)
- Output two formats per term: IPA notation (/ˌætɔːrvəˈstætɪn/) and a simplified readable guide (a-TOR-va-sta-tin)
- Expose a `get_pronunciation(term: str) -> dict` function returning both formats plus confidence

**Dictionary format**:
```python
MEDICAL_DICT = {
    "atorvastatin": {
        "ipa": "/eɪˌtɔːrvəˈstætɪn/",
        "simplified": "ay-TOR-va-STA-tin",
        "syllables": ["ay", "TOR", "va", "STA", "tin"],
        "stress": [1, 3]  # indices of stressed syllables
    }
}
```

---

### Feature 2: IPA Display on Translation Output

**Module**: `pronunciation/ipa_display.py`

**What it does**: After translation, scan the output text for medical terms and annotate them with their IPA pronunciation and simplified guide. Display inline in the UI.

**Implementation**:
- `MedicalTermDetector` class that scans translated text for known medical terms using fuzzy matching (handle plurals, conjugations)
- For each detected term, return: original term, position in text, IPA, simplified pronunciation
- API endpoint: `POST /api/pronunciation/annotate` accepts translated text, returns annotated version
- Frontend renders detected terms with a hover tooltip showing the pronunciation

**Frontend behavior**:
- Detected medical terms are underlined with the amber accent color
- Hovering shows a tooltip with: term, IPA, simplified guide, syllable breakdown
- A small speaker icon in the tooltip triggers browser TTS of the simplified pronunciation

---

### Feature 3: ASR Confidence Scoring Per Word

**Module**: `pronunciation/confidence.py`

**What it does**: Extracts word-level confidence scores from faster-whisper and flags low-confidence medical terms for human review.

**Implementation**:
- faster-whisper already returns word-level timestamps and probabilities — extract and expose these
- `ConfidenceAnalyzer` class that processes the whisper output segments
- Flag any word with confidence below 0.75 as uncertain
- Flag any medical term (from the dictionary) with confidence below 0.85 as high-risk (medical accuracy matters more)
- API response should include: `words: [{word, confidence, is_medical, flagged}]`

**Frontend behavior**:
- Flagged words are highlighted in the transcript with amber (uncertain) or red (high-risk medical)
- Overall confidence score displayed as a badge on the transcript card
- Tooltip on flagged word explains why it was flagged

---

### Feature 4: Human-in-the-Loop Correction and Feedback Store

**Module**: `feedback/correction_store.py`

**What it does**: When a user corrects a mistranscribed or mispronounced term, store the correction. Build a lightweight feedback loop that improves future suggestions.

**Implementation**:
- SQLite database (or JSON file for simplicity) to store corrections
- Schema: `{id, original_term, corrected_term, context_phrase, timestamp, source_language, target_language, user_confirmed}`
- `CorrectionStore` class with methods: `add_correction()`, `get_corrections_for_term()`, `get_all_corrections()`, `export_corrections()`
- Before each transcription, load stored corrections and use them to post-process Whisper output (simple string replacement for confirmed corrections)
- Admin endpoint: `GET /api/feedback/corrections` returns all stored corrections as JSON (for future model fine-tuning)

**Frontend behavior**:
- Inline edit on any transcribed word (click to edit)
- On edit confirmation, correction is stored and highlighted in green
- Small correction count badge on the app header showing total corrections stored
- Export button in settings that downloads corrections as CSV

---

### Feature 5: OOV (Out-of-Vocabulary) Detection and Logging

**Module**: `pronunciation/oov_detector.py`

**What it does**: Detect words that the ASR model is likely struggling with because they fall outside its training distribution, and log them for analysis.

**Implementation**:
- `OOVDetector` class that combines three signals:
  1. Low confidence score from Whisper (below 0.70)
  2. Term not found in any standard English word list (use `pyenchant` or a bundled wordlist)
  3. Term matches patterns common to OOV words (long compounds, foreign names, brand names, chemical suffixes like -statin, -mab, -pril, -olol, -zole)
- Log all detected OOV terms to a persistent store with: term, context, timestamp, detection signals
- Expose `GET /api/oov/log` endpoint returning the OOV log
- Expose `GET /api/oov/stats` returning counts by category

**Frontend behavior**:
- OOV terms shown with a distinct purple underline in the transcript
- Sidebar panel (collapsible) showing the OOV log for the current session
- Each OOV entry shows the term and why it was flagged

---

## API Structure

All new endpoints go under `/api/` prefix:

```
POST /api/transcribe          — existing, now returns word-level confidence
POST /api/translate           — existing, now returns annotated output
POST /api/pronunciation/annotate  — new: annotate text with IPA
POST /api/feedback/correction     — new: store a correction
GET  /api/feedback/corrections    — new: get all corrections
GET  /api/oov/log                 — new: get OOV log
GET  /api/oov/stats               — new: OOV stats
GET  /api/health                  — health check
```

---

## UI Layout

### Recording Screen (main view)
```
┌─────────────────────────────────────────┐
│  [Logo]          Healthcare Translation  │
├─────────────────────────────────────────┤
│                                         │
│     [Waveform visualizer — animated     │
│      amber wave while recording]        │
│                                         │
│     [● Record]  [■ Stop]  [Language ▼]  │
│                                         │
├─────────────────────────────────────────┤
│ TRANSCRIPT                [confidence]  │
│ "Patient has [atorvastatin] [pharynx]   │
│  inflammation..."                       │
│ (underlined terms = medical, flagged)   │
├─────────────────────────────────────────┤
│ TRANSLATION               [target lang] │
│ Translated text with same annotations  │
├─────────────────────────────────────────┤
│ [OOV Panel]  [Corrections: 3]  [Export] │
└─────────────────────────────────────────┘
```

### Pronunciation Tooltip (on hover)
```
┌──────────────────────────────┐
│ atorvastatin                 │
│ /eɪˌtɔːrvəˈstætɪn/          │
│ ay-TOR-va-STA-tin            │
│ ●○●○○ (stress pattern)       │
│ [🔊 Hear it]                 │
└──────────────────────────────┘
```

---

## Dependencies to Install

```bash
pip install g2p-en pyenchant eng-to-ipa faster-whisper flask flask-cors
```

Note: `pyenchant` requires the `enchant` C library. If unavailable, use the bundled `words_alpha.txt` wordlist from dwyl/english-words as a fallback.

---

## File Structure

```
healthcare-translation/
├── app.py                        # Flask entry point
├── config.py                     # Environment config
├── pronunciation/
│   ├── __init__.py
│   ├── g2p_medical.py            # Feature 1: G2P + medical dict
│   ├── ipa_display.py            # Feature 2: IPA annotation
│   ├── confidence.py             # Feature 3: confidence scoring
│   └── oov_detector.py           # Feature 5: OOV detection
├── feedback/
│   ├── __init__.py
│   └── correction_store.py       # Feature 4: feedback loop
├── data/
│   ├── medical_dictionary.py     # Extended medical term dict
│   └── corrections.db            # SQLite corrections store
├── static/
│   ├── css/
│   │   ├── tokens.css            # Design tokens (colors, spacing, type)
│   │   └── main.css              # Component styles
│   └── js/
│       ├── recorder.js           # Audio recording + waveform
│       ├── annotations.js        # Medical term highlighting
│       └── corrections.js        # Inline editing
└── templates/
    └── index.html                # Single page app shell
```

---

## Implementation Order

Build in this exact order so each feature is testable before moving on:

1. Read all existing files and understand the current architecture fully
2. Set up the new design system (tokens.css) based on portfolio folder + new color direction
3. Rebuild the UI shell with the new design (waveform visualizer last)
4. Build `g2p_medical.py` with the full medical dictionary and tests
5. Integrate Feature 1 into the translation response
6. Build `confidence.py` and integrate into the transcription response
7. Build `ipa_display.py` and the frontend annotation + tooltip
8. Build `correction_store.py` and the inline edit UI
9. Build `oov_detector.py` and the OOV sidebar panel
10. Build the waveform visualizer using the Web Audio API
11. Final pass: responsive layout, accessibility, performance

---

## Quality Bar

- Every new module must have a `if __name__ == "__main__"` test block with at least 3 test cases
- API endpoints must return consistent JSON with `{success, data, error}` envelope
- All medical term detections must be case-insensitive
- The UI must work on mobile (minimum 375px wide)
- No hardcoded colors in component CSS — all values from tokens.css
- The waveform must respect `prefers-reduced-motion` and show a static pulse instead

---

## Notes for Claude Code

- The portfolio folder path will be provided at runtime — read it before writing any CSS
- Do not delete or restructure the existing Whisper or Helsinki-NLP integration — extend it
- If a dependency fails to install, note it clearly and implement a graceful fallback
- Commit-worthy chunks: complete one feature fully (backend module + API endpoint + UI integration) before starting the next
- The medical dictionary is the most important single asset — take care building it out fully, it is what makes this app credible
