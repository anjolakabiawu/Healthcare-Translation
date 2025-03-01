from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
#import openai
from dotenv import load_dotenv
import os
#from google.cloud import speech_v1p1beta1 as speech
#from google.oauth2 import service_account
import deepl

app = Flask(__name__, static_folder="/workspaces/Healthcare-Translation/frontend/build", static_url_path="/")
#CORS(app, origins=["https://verbose-potato-p6j9q6x4gpc7495-3000.app.github.dev"]) # Enable CORS for frontend-backend communication

# Load environment variables from .env file
load_dotenv()

# Setting my OpenAI API key
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

if not deepseek_api_key:
    raise ValueError("DeepSeek API key not found. Please set the DEEPSEEK_API_KEY environment variable.")

translator = deepl.Translator(deepseek_api_key)
#print("OpenAI API Key:", os.getenv("OPENAI_API_KEY"))

# Google Speech-to-Text client
#credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
#credentials = service_account.Credentials.from_service_account_file(credentials_path)
#client = speech.SpeechClient(credentials=credentials)

@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

#@app.route('/transcribe', methods=['POST'])
#def transcribe():
 #   if 'audio' not in request.files:
#        return jsonify({"error": "No audio file provided"}), 400
    
#    audio_file = request.files['audio']
#    language = request.form.get('language', 'en-US')

    # Read the audio file
#    audio_content = audio_file.read()

    # Configure the audio file for Google Speech-to-Text
#    audio = speech.RecognitionAudio(content=audio_content)
#    config = speech.RecognitionConfig(
#        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
#        sample_rate_hertz=16000,
#        language_code=language,
#    )

    #Transcribe the audio
#    response = client.recognize(config=config, audio=audio)
#    if not response.results:
 #       return jsonify({"error": "No transcription results found"}), 400
    
#    transcript = response.results[0].alternatives[0].transcript
#    return jsonify({"transcript": transcript})

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    text = data.get('text')
    target_language = data.get('target_language', 'EN') # Default to English

    # Using DEEPSEEK for translation
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        # Use DeepSeek API for translation
        result = translator.translate_text(text, target_lang=target_language)
        translated_text = result.text
        return jsonify({"translated_text": translated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)