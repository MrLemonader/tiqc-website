from pathlib import Path

from flask import Flask, jsonify
from werkzeug.exceptions import RequestEntityTooLarge

from config import Config

from .extensions import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    Path(app.config["AVATAR_UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)

    from .auth import auth_bp
    from .routes.api import api_bp
    from .routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)

    register_cli(app)
    register_error_handlers(app)
    return app


def register_cli(app):
    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        print("Database tables created.")

    @app.cli.command("seed-db")
    def seed_db():
        from .seed import seed_demo_data

        seed_demo_data()
        print("Demo data seeded.")


def register_error_handlers(app):
    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(error):
        return jsonify({"error": "Uploaded file must be 20 MB or smaller"}), 413
