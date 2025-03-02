# Healthcare-Translation Web App

This is a web-based prototype that enables real-time, multilingual translation between patients and healthcare providers. The app converts spoken input into text, provides a live transcript, and offers a translated version with audio playback.

## Features
- **Voice-to-Text**: Converts spoken input into text using the Web Speech API.
- **Real-Time Translation**: Translates text using DeepL API.
- **Audio Playback**: Speaks the translated text using the Web Speech API.
- **Mobile-First Design**: Responsive and optimized for mobile and desktop use.
- **Translation History**: Saves and displays past translations.

## Technologies Used
- **Framework**: Flask (Backend & Frontend)
- **Translation API**: DeepL API
- **Speech Recognition**: Web Speech API
- **Security**: Flask-Talisman
- **UI Design**: HTML, CSS, JavaScript, Bootstrap
- **Deployment**: Render (Flask App)

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/anjolakabiawu/Healthcare-Translation.git
   cd Healthcare-Translation

2. Install dependencies:
    cd frontend
    npm install
    cd ../backend
    pip install -r requirements.txt

3. Set environment variables:
    Your DeepLAI API key

4. Run the app:
    python app.py