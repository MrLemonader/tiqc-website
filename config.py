import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


def resolve_project_path(value, default):
    path = Path(value or default)
    if not path.is_absolute():
        path = BASE_DIR / path
    return str(path.resolve())


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://tiqc:tiqc@127.0.0.1:3306/tiqc_profiles",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024
    UPLOAD_FOLDER = resolve_project_path(os.getenv("UPLOAD_FOLDER"), "uploads")
    AVATAR_UPLOAD_FOLDER = str(Path(UPLOAD_FOLDER) / "avatars")
    DEFAULT_CAMPUS_ID = os.getenv("DEFAULT_CAMPUS_ID", "")
