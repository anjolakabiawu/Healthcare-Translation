from flask import Blueprint, request, jsonify, session, current_app
from datetime import datetime, timezone
from ..services.translation import translation_service
from ..services.glossary import glossary_service
from ..pronunciation.ipa_display import term_detector

translate_bp = Blueprint("translate", __name__)


@translate_bp.route("/api/translate", methods=["POST"])
def translate():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    text = data.get("text", "").strip()
    source_lang = data.get("source_lang", "en").strip().lower()
    target_lang = data.get("target_lang", "").strip().lower()

    if not text:
        return jsonify({"error": "Missing required field: text"}), 400
    if not target_lang:
        return jsonify({"error": "Missing required field: target_lang"}), 400

    preprocessed = glossary_service.apply_glossary(text, source_lang, target_lang)

    try:
        result = translation_service.translate(preprocessed, source_lang, target_lang)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Translation error: {e}")
        return jsonify({"error": "Translation failed.", "details": str(e)}), 500

    highlighted_original = glossary_service.highlight_terms(text, source_lang, target_lang)
    highlighted_translated = glossary_service.highlight_translated_terms(
        result["translated_text"], source_lang, target_lang
    )

    # Annotate whichever side is English with IPA pronunciation tooltips.
    # The medical dictionary is English-keyed, so only annotate English text.
    pron_terms = []
    annotated_original = None
    if source_lang == "en":
        ann = term_detector.annotate(text)
        annotated_original = ann["annotated_html"]
        pron_terms = ann["terms"]
    elif target_lang == "en":
        ann = term_detector.annotate(result["translated_text"])
        pron_terms = ann["terms"]

    timestamp = datetime.now(timezone.utc).isoformat()

    entry = {
        "original_text": text,
        "translated_text": result["translated_text"],
        "highlighted_original": highlighted_original,
        "highlighted_translated": highlighted_translated,
        "annotated_original": annotated_original,
        "pronunciation_terms": pron_terms,
        "source_lang": source_lang,
        "target_lang": target_lang,
        "timestamp": timestamp,
    }

    if "history" not in session:
        session["history"] = []
    session["history"].append(entry)
    session.modified = True

    return jsonify(entry)
