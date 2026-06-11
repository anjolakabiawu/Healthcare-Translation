# Healthcare Translation Web App - User Guide

This guide will walk you through how to use the Healthcare Translation Web App.

---

## **Features**

- **Voice-to-Text**: Convert spoken input into text.
- **Real-Time Translation**: Translate text into multiple languages.
- **Medical Pronunciation Help**: See how to say medical terms correctly, with a "Hear it" button.
- **Audio Playback**: Listen to the translated text.
- **Translation History**: View past translations.

---

## **How to Use the App**

### **1. Choose Your Languages**

- Use the **From** dropdown to pick the language you'll speak or type in.
- Use the **To** dropdown to pick the language you want the translation in.
- The **swap** button between them flips the two languages.

### **2. Enter the Text**

- **Type** directly into the **Clinical Notes / Patient Speech** box, **or**
- Click **Record** and start speaking — your words appear in the box as you talk.
  Click **Stop** (or just pause) to finish. While recording, an amber **waveform**
  animates to show the app is listening.

### **3. Translate**

- Click the **Translate** button.
- The result appears in two columns: **Original** on the left, **Translation** on the right.

### **4. Check Pronunciations**

- In the **Original** column, medical terms are **underlined in amber**.
- **Hover** (or tap) an underlined term to see a tooltip with:
  - the term's **IPA** (e.g. `/eɪˌtɔːrvəˈstætɪn/`),
  - a **simplified guide** (e.g. `ay-TOR-va-STA-tin`),
  - dots showing the **stress pattern**, and
  - a **Hear it** button that reads the term aloud.

### **5. Listen to the Translation**

- Click the **speaker** icon above the translation to hear the full translated text.
- Click the **copy** icon to copy the translation to your clipboard.

### **6. View Translation History**

- Click the **History** tab at the top to see your past translations.
- Use **Clear All** to remove them.

---

## **Supported Languages**

English, Spanish, French, German, Chinese, Portuguese, Arabic, and Russian — available as both input and output languages.

> Pronunciation tooltips are provided for **English** medical terms.

---

## **Troubleshooting**

- **Transcription is slow on first use**: The speech model can take up to a minute to load the first time after the server starts. Subsequent uses are much faster.
- **No microphone / waveform won't appear**: Allow microphone access when your browser prompts. Recording also requires a Chromium-based browser (Chrome or Edge) for in-browser speech recognition.
- **Translation failed**: Translation runs locally, so it doesn't need the internet — but the model must finish loading. If it fails, wait a moment and try again.
- **No pronunciation tooltip on a term**: Only terms in the medical dictionary are annotated. Unrecognized terms simply won't be underlined.

---

## **Privacy and Security**

- Speech recognition and translation run **locally** on the server — your text is not sent to a third-party translation service.
- Translation history is stored only in your browser session and clears when the session ends.
- The app uses Flask-Talisman security headers.

---

## **Contact Support**

If you encounter any issues, please contact support at [anjolakabiawu6@gmail.com](mailto:anjolakabiawu6@gmail.com).
