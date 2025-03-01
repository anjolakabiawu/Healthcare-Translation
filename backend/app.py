from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from dotenv import load_dotenv
import os
from google.cloud import speech_v1p1beta1 as speech
from google.oauth2 import service_account

app = Flask(__name__, static_folder="/workspaces/Healthcare-Translation/frontend/build", static_url_path="/")
CORS(app) # Enable CORS for frontend-backend communication

# Setting my OpenAI API key
openai.api_key = ""

# Load environment variables from .env file
load_dotenv()

# Google Speech-to-Text client
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
credentials = service_account.Credentials.from_service_account_file(credentials_path)
client = speech.SpeechClient(credentials=credentials)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = request.files['audio']
    language = request.form.get('language', 'en-US')

    # Read the audio file
    audio_content = audio_file.read()

    # Configure the audio file for Google Speech-to-Text
    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=language,
    )

    #Transcribe the audio
    response = client.recognize(config=config, audio=audio)
    if not response.results:
        return jsonify({"error": "No transcription results found"}), 400
    
    transcript = response.results[0].alternatives[0].transcript
    return jsonify({"transcript": transcript})

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    text = data.get('text')
    target_language = data.get('target_language', 'English') # Default to English

    # Using OpenAI for translation
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role":"user", "content":f"Translate the following text to {target_language}: {text}"}
            ]
        )
        translated_text = response.choices[0].message.content
        return jsonify({"translated_text": translated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)