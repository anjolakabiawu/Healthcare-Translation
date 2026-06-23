from flask import Blueprint, request, jsonify, Response, current_app

from ..feedback.correction_store import correction_store

feedback_bp = Blueprint("feedback", __name__)


def _ok(data):
    return jsonify({"success": True, "data": data, "error": None})


def _err(message, status=400):
    return jsonify({"success": False, "data": None, "error": message}), status


@feedback_bp.route("/api/feedback/correction", methods=["POST"])
def add_correction():
    data = request.get_json(silent=True)
    if not data:
        return _err("Request body must be JSON.")

    original = (data.get("original_term") or "").strip()
    corrected = (data.get("corrected_term") or "").strip()
    if not original or not corrected:
        return _err("original_term and corrected_term are required")

    try:
        rid = correction_store.add_correction(
            original_term=original,
            corrected_term=corrected,
            context_phrase=(data.get("context_phrase") or "").strip(),
            source_language=(data.get("source_language") or "").strip().lower(),
            target_language=(data.get("target_language") or "").strip().lower(),
        )
    except ValueError as e:
        return _err(str(e))
    except Exception as e:
        current_app.logger.error(f"Correction store error: {e}")
        return _err("Could not store correction.", 500)

    return _ok({"id": rid, "count": correction_store.count()})


@feedback_bp.route("/api/feedback/corrections", methods=["GET"])
def list_corrections():
    return _ok({
        "corrections": correction_store.get_all_corrections(),
        "count": correction_store.count(),
    })


@feedback_bp.route("/api/feedback/corrections/export", methods=["GET"])
def export_corrections():
    csv_text = correction_store.export_corrections()
    return Response(
        csv_text,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=corrections.csv"},
    )
