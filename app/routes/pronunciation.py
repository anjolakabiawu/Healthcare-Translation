from flask import Blueprint, request, jsonify, current_app

from ..pronunciation.ipa_display import term_detector
from ..pronunciation.g2p_medical import get_pronunciation

pronunciation_bp = Blueprint("pronunciation", __name__)


def _ok(data):
    return jsonify({"success": True, "data": data, "error": None})


def _err(message, status=400):
    return jsonify({"success": False, "data": None, "error": message}), status


@pronunciation_bp.route("/api/pronunciation/annotate", methods=["POST"])
def annotate():
    data = request.get_json(silent=True)
    if not data:
        return _err("Request body must be JSON.")

    text = (data.get("text") or "").strip()
    if not text:
        return _err("Missing required field: text")

    try:
        result = term_detector.annotate(text)
    except Exception as e:
        current_app.logger.error(f"Annotation error: {e}")
        return _err("Annotation failed.", 500)

    return _ok(result)


@pronunciation_bp.route("/api/pronunciation/term", methods=["GET"])
def term():
    """Lightweight single-term lookup used by the tooltip's fallback path."""
    q = (request.args.get("term") or "").strip()
    if not q:
        return _err("Missing required query param: term")
    return _ok(get_pronunciation(q))
