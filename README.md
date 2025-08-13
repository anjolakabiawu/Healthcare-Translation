# Healthcare-Translation Web App

This is a web-based prototype that enables real-time, multilingual translation between patients and healthcare providers. The app converts spoken input into text, provides a live transcript, and offers a translated version with audio playback.

## Features
- **Voice-to-Text**: Converts spoken input into text using the `openai/whisper-tiny` model run locally.
- **Real-Time Translation**: Translates text using the DeepL API.
- **Audio Playback**: Speaks the translated text using the Web Speech API.
- **Mobile-First Design**: Responsive and optimized for mobile and desktop use.
- **Translation History**: Saves and displays past translations.

## Technologies Used
- **Framework**: Flask (Backend & Frontend)
- **Speech Recognition**: `transformers` library (Hugging Face) with `PyTorch` to run the Whisper model.
- **Translation API**: DeepL API
- **Security**: Flask-Talisman
- **UI Design**: HTML, CSS, JavaScript
- **Deployment**: Render (Flask App)

## Setup
1. Clone the repository:
   ```bash
   git clone [https://github.com/anjolakabiawu/Healthcare-Translation.git](https://github.com/anjolakabiawu/Healthcare-Translation.git)
   cd Healthcare-Translation
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set environment variables:
    ```bash
    export DEEPL_API_KEY="your_deepl_api_key_goes_here"
    export HUGGINGFACE_API_TOKEN="hf_your_huggingface_token_goes_here"
    ```

4. Run the app:
    ```bash
    python app.py
    ```