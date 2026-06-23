from flask import Blueprint, request, jsonify, current_app
from ..services.transcription import transcription_service
from ..pronunciation.confidence import confidence_analyzer

transcribe_bp = Blueprint("transcribe", __name__)

MAX_BYTES = 10 * 1024 * 1024  # 10 MB


@transcribe_bp.route("/api/transcribe", methods=["POST"])
def transcribe():
    audio_data = request.data
    if not audio_data:
        return jsonify({"error": "No audio data received."}), 400

    if len(audio_data) > MAX_BYTES:
        return jsonify({"error": "Audio file too large. Maximum size is 10 MB."}), 413

    content_type = request.content_type or ""
    if not content_type.startswith("audio/") and content_type not in ("application/octet-stream", ""):
        return jsonify({"error": "Invalid content type. Expected audio/*."}), 415

    model_size = current_app.config.get("WHISPER_MODEL_SIZE", "tiny")
    if transcription_service.model_size != model_size:
        transcription_service.model_size = model_size
        transcription_service._model = None  # force reload only if size changed

    try:
        result = transcription_service.transcribe(audio_data)
        analysis = confidence_analyzer.analyze(result.get("words", []))
        return jsonify({
            "text": result["text"],
            "detected_language": result["language"],
            "confidence": result["confidence"],
            "words": analysis["words"],
            "overall_confidence": analysis["overall_confidence"],
            "flagged_count": analysis["flagged_count"],
            "high_risk_count": analysis["high_risk_count"],
        })
    except Exception as e:
        current_app.logger.error(f"Transcription error: {e}")
        return jsonify({"error": "Transcription failed.", "details": str(e)}), 500
