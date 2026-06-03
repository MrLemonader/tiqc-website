from flask import Blueprint, current_app, jsonify, send_from_directory

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@main_bp.route("/members")
@main_bp.route("/members/<path:slug>")
@main_bp.route("/profile")
def spa_placeholder(slug=None):
    return jsonify(
        {
            "message": "Vue SPA frontend is not built yet.",
            "api": {
                "members": "/api/members",
                "profile": "/api/profile",
                "me": "/api/me",
            },
        }
    )


@main_bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
