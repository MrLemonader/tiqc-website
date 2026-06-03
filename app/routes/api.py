from flask import Blueprint, jsonify, request

from ..auth import get_current_member
from ..models import Member
from ..services.profile_service import update_member_profile
from ..services.upload_service import save_avatar

api_bp = Blueprint("api", __name__, url_prefix="/api")


def login_required_response():
    return jsonify({"error": "login_required"}), 401


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
    from flask import g

    if not g.current_user:
        return login_required_response()
    return jsonify({"user": g.current_user.to_dict()})


@api_bp.route("/profile", methods=["GET", "PATCH"])
def profile():
    member = get_current_member()
    if not member:
        return login_required_response()

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
    member = get_current_member()
    if not member:
        return login_required_response()

    try:
        avatar_url = save_avatar(member, request.files.get("avatar"))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"avatar_url": avatar_url})
