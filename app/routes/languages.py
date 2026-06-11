from flask import Blueprint, jsonify
from ..services.translation import translation_service, SUPPORTED_PAIRS

languages_bp = Blueprint("languages", __name__)

LANGUAGE_NAMES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese",
    "pt": "Portuguese",
    "ar": "Arabic",
    "ru": "Russian",
}


@languages_bp.route("/api/languages", methods=["GET"])
def get_languages():
    pairs = [
        {
            "source": s,
            "source_name": LANGUAGE_NAMES.get(s, s.upper()),
            "target": t,
            "target_name": LANGUAGE_NAMES.get(t, t.upper()),
        }
        for (s, t) in sorted(SUPPORTED_PAIRS)
    ]
    unique_langs = {}
    for code, name in LANGUAGE_NAMES.items():
        unique_langs[code] = name

    return jsonify({"pairs": pairs, "languages": unique_langs})
