# Healthcare-Translation Web App

This is a web-based prototype that enables real-time, multilingual translation between patients and healthcare providers. The app converts spoken input into text, provides a live transcript, and offers a translated version with audio playback.

## Features
- **Voice-to-Text**: Converts spoken input into text using Google Speech-to-Text.
- **Real-Time Translation**: Translates text using OpenAI GPT-4.
- **Audio Playback**: Speaks the translated text using the Web Speech API.
- **Mobile-First Design**: Responsive and optimized for mobile and desktop use.
- **Translation History**: Saves and displays past translations.

## Technologies Used
- **Frontend**: React.js, React-Bootstrap
- **Backend**: Flask, Google Speech-to-Text, OpenAI GPT-4
- **Deployment**: Vercel (Frontend), Render (Backend)

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/anjolakabiawu/Healthcare-Translation.git

2. Install dependencies:
    cd frontend
    npm install
    cd ../backend
    pip install -r requirements.txt

3. Set environment variables:
    Your OpenAI API key
    Path to your Google Cloud credentials JSON file

4. Run the app:
    cd backend
    python app.py

    cd frontend
    npm start