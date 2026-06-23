from flask import Blueprint, request, jsonify, current_app
from ..services.transcription import transcription_service
from ..pronunciation.confidence import confidence_analyzer
from ..pronunciation.oov_detector import oov_detector
from ..feedback.correction_store import correction_store

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

        # Apply confirmed human corrections to the raw transcript (Feature 4).
        text = correction_store.apply_corrections(result["text"], result.get("language"))

        # Per-word confidence scoring (Feature 3).
        analysis = confidence_analyzer.analyze(result.get("words", []))

        # OOV detection + logging for this utterance (Feature 5).
        oov_hits = oov_detector.analyze(result.get("words", []), context=text)

        return jsonify({
            "text": text,
            "detected_language": result["language"],
            "confidence": result["confidence"],
            "words": analysis["words"],
            "overall_confidence": analysis["overall_confidence"],
            "flagged_count": analysis["flagged_count"],
            "high_risk_count": analysis["high_risk_count"],
            "oov_terms": oov_hits,
            "correction_count": correction_store.count(),
        })
    except Exception as e:
        current_app.logger.error(f"Transcription error: {e}")
        return jsonify({"error": "Transcription failed.", "details": str(e)}), 500
