from flask import Flask, render_template, request, jsonify
from flask_talisman import Talisman
from dotenv import load_dotenv
import os
import deepl

# Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")

# Flask-Talisman for Security (No CORS Required)
Talisman(app, content_security_policy=None)

# Load API Key
load_dotenv()
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
if not deepseek_api_key:
    raise ValueError("DeepSeek API key not found. Please set the DEEPSEEK_API_KEY environment variable.")

translator = deepl.Translator(deepseek_api_key)

DEEPL_LANGUAGES = {
    "EN-US", "BG", "CS", "DA", "DE", "EL", "ES", "ET", "FI", "FR",
    "HU", "ID", "IT", "JA", "KO", "LT", "LV", "NB", "NL", "PL",
    "PT-PT", "RO", "RU", "SK", "SL", "SV", "TR", "UK", "ZH-HANS"
}

# ✅ Serve HTML Page from Flask
@app.route("/")
def index():
    return render_template("index.html")  # Serve frontend

# ✅ Translation API
@app.route("/api/translate", methods=["POST"])
def translate():
    data = request.json
    if not data or "text" not in data or "target_language" not in data:
        return jsonify({"error": "Invalid request. Missing text or target language."}), 400

    text = data["text"]
    target_language = data["target_language"].upper()  # Convert to uppercase

    # ✅ Validate target language
    if target_language not in DEEPL_LANGUAGES:
        return jsonify({"error": f"Unsupported target language: {target_language}"}), 400

    try:
        result = translator.translate_text(text, target_lang=target_language)
        return jsonify({"translated_text": result.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
