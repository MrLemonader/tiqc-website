from flask import Blueprint, g, make_response, redirect, request

from .models import User

auth_bp = Blueprint("auth", __name__)


def get_current_user():
    campus_id = request.cookies.get("campus_id")
    if not campus_id:
        return None
    return User.query.filter_by(campus_id=campus_id).first()


def get_current_member():
    user = getattr(g, "current_user", None) or get_current_user()
    return user.member if user and user.member else None


@auth_bp.before_app_request
def load_current_user():
    g.current_user = get_current_user()
    g.current_member = g.current_user.member if g.current_user and g.current_user.member else None


@auth_bp.route("/dev-login/<campus_id>")
def dev_login(campus_id):
    response = make_response(redirect("/profile"))
    response.set_cookie("campus_id", campus_id, httponly=True, samesite="Lax")
    return response


@auth_bp.route("/dev-logout")
def dev_logout():
    response = make_response(redirect("/"))
    response.delete_cookie("campus_id")
    return response
