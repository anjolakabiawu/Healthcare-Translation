from flask import Blueprint, jsonify

from ..pronunciation.oov_detector import oov_detector

oov_bp = Blueprint("oov", __name__)


def _ok(data):
    return jsonify({"success": True, "data": data, "error": None})


@oov_bp.route("/api/oov/log", methods=["GET"])
def oov_log():
    return _ok({"log": oov_detector.get_log()})


@oov_bp.route("/api/oov/stats", methods=["GET"])
def oov_stats():
    return _ok(oov_detector.get_stats())
