from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
import deepl

app = Flask(__name__, static_folder="build", static_url_path="/")
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": ["https://healthcare-translation-yy1x-ocoswhv1f.vercel.app"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"],
        }
    },
)

# Load environment variables from .env file
load_dotenv()

# Setting my Deepseek API key
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

if not deepseek_api_key:
    raise ValueError("DeepSeek API key not found. Please set the DEEPSEEK_API_KEY environment variable.")

translator = deepl.Translator(deepseek_api_key)

@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# Handle preflight requests for /api/translate
@app.route("/api/translate", methods=["OPTIONS"])
def handle_preflight():
    response = jsonify({"message": "Preflight request handled"})
    response.headers.add("Access-Control-Allow-Origin", "https://healthcare-translation-yy1x-ocoswhv1f.vercel.app")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    return response

@app.route("/api/translate", methods=["POST"])
def translate():
    data = request.json
    text = data.get("text")
    target_language = data.get("target_language", "EN-US")
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        result = translator.translate_text(text, target_lang=target_language)
        return jsonify({"translated_text": result.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Health check endpoint
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})

@app.route("/env")
def show_env():
    return jsonify({
        "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY")
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)