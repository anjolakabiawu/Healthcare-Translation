from flask import Flask, jsonify
from flask_talisman import Talisman
from flask_cors import CORS
from .config import config_map


def create_app(config_name="development"):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_map[config_name])

    CORS(app)
    Talisman(app, content_security_policy=None, force_https=False)

    from .routes.main import main_bp
    from .routes.transcribe import transcribe_bp
    from .routes.translate import translate_bp
    from .routes.history import history_bp
    from .routes.languages import languages_bp
    from .routes.pronunciation import pronunciation_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(transcribe_bp)
    app.register_blueprint(translate_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(languages_bp)
    app.register_blueprint(pronunciation_bp)

    @app.route("/api/health")
    def health():
        return jsonify({"success": True, "data": {"status": "ok"}, "error": None})

    # Warm up the Whisper model in a background thread so first request is fast
    if not app.config.get("TESTING"):
        import threading
        from .services.transcription import transcription_service

        def _warmup():
            try:
                transcription_service.model_size = app.config.get("WHISPER_MODEL_SIZE", "tiny")
                transcription_service._get_model()
            except Exception as e:  # never let model warmup crash the server
                app.logger.warning(f"Whisper warmup failed (will retry on first request): {e}")

        threading.Thread(target=_warmup, daemon=True).start()

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request", "details": str(e)}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app
