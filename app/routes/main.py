from pathlib import Path

from flask import Blueprint, current_app, make_response, send_from_directory

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@main_bp.route("/login")
@main_bp.route("/members")
@main_bp.route("/members/<path:slug>")
@main_bp.route("/profile")
def spa_entry(slug=None):
    frontend_dist = Path(current_app.config["FRONTEND_DIST_FOLDER"])
    index_file = frontend_dist / "index.html"
    if not index_file.exists():
        return make_response(
            "Vue frontend build not found. Run `npm install` and `npm run build` "
            "inside the frontend directory before using Flask as the production entry.",
            503,
        )
    return send_from_directory(frontend_dist, "index.html")


@main_bp.route("/assets/<path:filename>")
def frontend_asset(filename):
    return send_from_directory(
        Path(current_app.config["FRONTEND_DIST_FOLDER"]) / "assets", filename
    )


@main_bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
