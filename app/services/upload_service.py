from pathlib import Path

from flask import current_app
from werkzeug.utils import secure_filename

from ..extensions import db

ALLOWED_AVATAR_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def save_avatar(member, uploaded_file):
    if not uploaded_file or not uploaded_file.filename:
        raise ValueError("No file uploaded")

    filename = secure_filename(uploaded_file.filename)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_AVATAR_EXTENSIONS:
        raise ValueError("Avatar must be jpg, jpeg, png, or webp")

    member_dir = Path(current_app.config["AVATAR_UPLOAD_FOLDER"]) / str(member.id)
    member_dir.mkdir(parents=True, exist_ok=True)
    cleanup_existing_avatars(member_dir)
    avatar_path = member_dir / f"avatar.{ext}"
    uploaded_file.save(avatar_path)

    member.avatar_url = f"/uploads/avatars/{member.id}/avatar.{ext}"
    db.session.commit()
    return member.avatar_url


def cleanup_existing_avatars(member_dir):
    for ext in ALLOWED_AVATAR_EXTENSIONS:
        avatar_path = member_dir / f"avatar.{ext}"
        if avatar_path.exists():
            avatar_path.unlink()
