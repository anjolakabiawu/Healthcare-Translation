from flask import Flask, render_template, request, jsonify
from flask_talisman import Talisman
from dotenv import load_dotenv
import os
import deepl
import requests
import pandas as pd

# Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")


# Flask-Talisman for Security
Talisman(app, content_security_policy=None)

# Load API Key
load_dotenv()
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
hugging_face_api_key = os.getenv("HUGGING_FACE_API_KEY")

# Check if API keys are set
if not deepseek_api_key or not hugging_face_api_key:
    raise ValueError("API key not found. Please set DEEPSEEK_API_KEY and HUGGING_FACE_API_KEY.")


translator = deepl.Translator(deepseek_api_key)

DEEPL_LANGUAGES = {
    "EN-US": "English (US)", "BG" : "Bulgarian", "CS" : "Czech", "DA" : "Danish", "DE" : "German",
    "EL" : "Greek", "ES" : "Spanish", "ET" : "Estonian", "FI" : "Finnish", "FR" : "French",
    "HU" : "Hungarian", "ID" : "Indonesian", "IT" : "Italian", "JA" : "Japanese", "KO" : "Korean",
    "LT" : "Lithuanian", "LV" : "Latvian", "NB" : "Norwegian Bokmål", "NL" : "Dutch", "PL" : "Polish",
    "PT-PT" : "Portuguese (Portugal)", "RO" : "Romanian", "RU" : "Russian", "SK" : "Slovak",
    "SL" : "Slovenian", "SV" : "Swedish", "TR" : "Turkish", "UK" : "Ukrainian", "ZH-HANS" : "Chinese (Simplified)"
    }

WHISPER_API_URL = "https://huggingface.co/openai/whisper-large-v3-turbo"
HF_API_HEADERS = {"Authorization": f"Bearer {hugging_face_api_key}",
                  "Content-Type": "audio/wav"}

glossary_df = None
try:
    # Load glossary from CSV file
    glossary_df = pd.read_csv("glossary.csv", header=None, names=["source", "target"])
    glossary_dict = dict(zip(glossary_df["source"], glossary_df["target"]))
except FileNotFoundError:
    print("WARNING: glossary.csv not found. No manual glossary will be applied.")
    glossary_dict = {}

def apply_manual_glossary(text, glossary):
    """
    A simple function to find and replace terms before translation.
    """
    for source_term, target_term in glossary.items():
        text = text.replace(source_term, target_term)
    return text



# Serve HTML Page from Flask
@app.route("/")
def index():
    return render_template("index.html", languages=DEEPL_LANGUAGES)  # Serve frontend

# Transcribe Audio using Whisper API
@app.route("/api/transcribe", methods=["POST"])
def transcribe():
    """Receives audio data and returns a transcription from Whisper."""
    if not request.data:
        return jsonify({"error": "No audio data received."}), 400
    
    try:
        response = requests.post(WHISPER_API_URL, headers=HF_API_HEADERS, data=request.data)
        response.raise_for_status()
        result = response.json()
        
        if "text" not in result:
            return jsonify({"error": "Transcription failed."}), 500
        
        return jsonify(result)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API request error: {str(e)}"}), 500

# Translation API
@app.route("/api/translate", methods=["POST"])
def translate():
    """Receives text and returns a translation from DeepL."""
    data = request.json
    if not data or "text" not in data or "target_language" not in data:
        return jsonify({"error": "Invalid request. Missing text or target language."}), 400

    text = data["text"]
    target_language = data["target_language"].upper() 
    
    text_with_glossary = apply_manual_glossary(text, glossary_dict)

    # Validate target language
    if target_language not in DEEPL_LANGUAGES:
        return jsonify({"error": f"Unsupported target language: {target_language}"}), 400

    try:
        result = translator.translate_text(text, target_lang=target_language)
        return jsonify({"translated_text": result.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
