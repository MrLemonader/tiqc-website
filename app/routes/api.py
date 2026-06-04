from flask import Blueprint, g, jsonify, make_response, request

from ..auth import get_current_member
from ..models import Member, User
from ..services.profile_service import update_member_profile
from ..services.upload_service import save_avatar

api_bp = Blueprint("api", __name__, url_prefix="/api")


def login_required_response():
    return jsonify({"error": "login_required"}), 401


def member_profile_required_response():
    return jsonify({"error": "member_profile_not_found"}), 404


@api_bp.route("/login", methods=["POST"])
def login():
    payload = request.get_json(silent=True) or {}
    campus_id = str(payload.get("campus_id", "")).strip()
    if not campus_id:
        return jsonify({"error": "campus_id_required"}), 400

    user = User.query.filter_by(campus_id=campus_id).first()
    if not user:
        return jsonify({"error": "invalid_campus_id"}), 401

    response = make_response(jsonify({"user": user.to_dict()}))
    response.set_cookie("campus_id", campus_id, httponly=True, samesite="Lax")
    return response


@api_bp.route("/logout", methods=["POST"])
def logout():
    response = make_response(jsonify({"ok": True}))
    response.delete_cookie("campus_id")
    return response


@api_bp.route("/members")
def members():
    member_list = (
        Member.query.filter_by(active=True)
        .order_by(Member.display_order.asc(), Member.name.asc())
        .all()
    )
    return jsonify(
        {"members": [member.to_dict(include_publications=False) for member in member_list]}
    )


@api_bp.route("/members/<slug>")
def member_detail(slug):
    member = Member.query.filter_by(slug=slug, active=True).first()
    if not member:
        return jsonify({"error": "member_not_found"}), 404
    return jsonify({"member": member.to_dict()})


@api_bp.route("/me")
def me():
    if not g.current_user:
        return login_required_response()
    return jsonify({"user": g.current_user.to_dict()})


@api_bp.route("/profile", methods=["GET", "PATCH"])
def profile():
    if not g.current_user:
        return login_required_response()

    member = get_current_member()
    if not member:
        return member_profile_required_response()

    if request.method == "GET":
        return jsonify({"member": member.to_dict()})

    payload = request.get_json(silent=True) or {}
    try:
        update_member_profile(member, payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"member": member.to_dict()})


@api_bp.route("/profile/avatar", methods=["POST"])
def profile_avatar():
    if not g.current_user:
        return login_required_response()

    member = get_current_member()
    if not member:
        return member_profile_required_response()

    try:
        avatar_url = save_avatar(member, request.files.get("avatar"))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"avatar_url": avatar_url})
