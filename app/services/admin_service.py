from ..extensions import db
from ..models import Member, User

USER_ROLES = {"member", "admin"}
MEMBER_ROLES = {"pi", "postdoc", "phd", "master", "undergrad", "alumni"}


class AdminServiceError(ValueError):
    pass


def create_user(campus_id, name, email=None, role="member", password=None):
    campus_id = normalize_required(campus_id, "campus_id")
    name = normalize_required(name, "name")
    role = normalize_choice(role or "member", USER_ROLES, "role")
    password = normalize_required(password if password is not None else campus_id, "password")

    if User.query.filter_by(campus_id=campus_id).first():
        raise AdminServiceError(f"User campus_id already exists: {campus_id}")

    user = User(campus_id=campus_id, name=name, email=normalize_optional(email), role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def create_member(
    user_campus_id,
    slug,
    role,
    campus_id=None,
    name=None,
    title=None,
    email=None,
    display_order=100,
    active=True,
):
    user_campus_id = normalize_required(user_campus_id, "user_campus_id")
    user = User.query.filter_by(campus_id=user_campus_id).first()
    if not user:
        raise AdminServiceError(f"User not found: {user_campus_id}")
    if user.member:
        raise AdminServiceError(f"User already has a member profile: {user_campus_id}")

    campus_id = normalize_required(campus_id or user.campus_id, "campus_id")
    slug = normalize_required(slug, "slug")
    role = normalize_choice(role, MEMBER_ROLES, "role")
    name = normalize_required(name or user.name, "name")

    ensure_unique_member_fields(campus_id=campus_id, slug=slug)

    member = Member(
        user_id=user.id,
        campus_id=campus_id,
        name=name,
        slug=slug,
        role=role,
        title=normalize_optional(title),
        email=normalize_optional(email) if email is not None else user.email,
        display_order=display_order,
        active=active,
    )
    db.session.add(member)
    db.session.commit()
    return member


def update_member(slug, **updates):
    slug = normalize_required(slug, "slug")
    member = Member.query.filter_by(slug=slug).first()
    if not member:
        raise AdminServiceError(f"Member not found: {slug}")

    if "new_slug" in updates and updates["new_slug"] is not None:
        new_slug = normalize_required(updates["new_slug"], "new_slug")
        existing = Member.query.filter_by(slug=new_slug).first()
        if existing and existing.id != member.id:
            raise AdminServiceError(f"Member slug already exists: {new_slug}")
        member.slug = new_slug

    if "name" in updates and updates["name"] is not None:
        member.name = normalize_required(updates["name"], "name")
    if "role" in updates and updates["role"] is not None:
        member.role = normalize_choice(updates["role"], MEMBER_ROLES, "role")
    if "title" in updates and updates["title"] is not None:
        member.title = normalize_optional(updates["title"])
    if "email" in updates and updates["email"] is not None:
        member.email = normalize_optional(updates["email"])
    if "display_order" in updates and updates["display_order"] is not None:
        member.display_order = updates["display_order"]
    if "active" in updates and updates["active"] is not None:
        member.active = updates["active"]

    db.session.commit()
    return member


def list_users():
    return User.query.order_by(User.campus_id.asc()).all()


def list_members():
    return Member.query.order_by(Member.display_order.asc(), Member.name.asc()).all()


def ensure_unique_member_fields(campus_id, slug):
    if Member.query.filter_by(campus_id=campus_id).first():
        raise AdminServiceError(f"Member campus_id already exists: {campus_id}")
    if Member.query.filter_by(slug=slug).first():
        raise AdminServiceError(f"Member slug already exists: {slug}")


def normalize_required(value, field_name):
    value = str(value or "").strip()
    if not value:
        raise AdminServiceError(f"{field_name} is required")
    return value


def normalize_optional(value):
    value = str(value).strip() if value is not None else None
    return value or None


def normalize_choice(value, allowed, field_name):
    value = normalize_required(value, field_name)
    if value not in allowed:
        allowed_values = ", ".join(sorted(allowed))
        raise AdminServiceError(f"{field_name} must be one of: {allowed_values}")
    return value
