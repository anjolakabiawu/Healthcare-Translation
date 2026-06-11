from flask import Blueprint, jsonify, session

history_bp = Blueprint("history", __name__)


@history_bp.route("/api/history", methods=["GET"])
def get_history():
    return jsonify(session.get("history", []))


@history_bp.route("/api/history", methods=["DELETE"])
def clear_history():
    session.pop("history", None)
    session.modified = True
    return jsonify({"message": "History cleared."})
