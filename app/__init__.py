from pathlib import Path

import click
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

    @app.cli.command("create-user")
    @click.option("--campus-id", required=True, help="Unique campus account ID.")
    @click.option("--name", required=True, help="User display name.")
    @click.option("--email", default=None, help="Optional contact email.")
    @click.option(
        "--role",
        default="member",
        show_default=True,
        type=click.Choice(["admin", "member"]),
        help="System role.",
    )
    def create_user_command(campus_id, name, email, role):
        from .services.admin_service import AdminServiceError, create_user

        try:
            user = create_user(campus_id=campus_id, name=name, email=email, role=role)
        except AdminServiceError as exc:
            raise click.ClickException(str(exc)) from exc
        click.echo(format_user(user))

    @app.cli.command("create-member")
    @click.option(
        "--user-campus-id",
        required=True,
        help="Campus ID of the existing user to bind.",
    )
    @click.option("--slug", required=True, help="Unique profile URL slug.")
    @click.option(
        "--role",
        required=True,
        type=click.Choice(["alumni", "master", "phd", "pi", "postdoc", "undergrad"]),
        help="Member role shown on the profile.",
    )
    @click.option("--campus-id", default=None, help="Member campus ID override.")
    @click.option("--name", default=None, help="Member name override.")
    @click.option("--title", default=None, help="Optional member title.")
    @click.option("--email", default=None, help="Optional contact email override.")
    @click.option("--display-order", default=100, show_default=True, type=int)
    @click.option(
        "--active",
        default="true",
        show_default=True,
        type=click.Choice(["false", "true"]),
        help="Whether this member appears in public member pages.",
    )
    def create_member_command(
        user_campus_id,
        slug,
        role,
        campus_id,
        name,
        title,
        email,
        display_order,
        active,
    ):
        from .services.admin_service import AdminServiceError, create_member

        try:
            member = create_member(
                user_campus_id=user_campus_id,
                slug=slug,
                role=role,
                campus_id=campus_id,
                name=name,
                title=title,
                email=email,
                display_order=display_order,
                active=parse_cli_bool(active),
            )
        except AdminServiceError as exc:
            raise click.ClickException(str(exc)) from exc
        click.echo(format_member(member))

    @app.cli.command("update-member")
    @click.option("--slug", required=True, help="Current member slug to update.")
    @click.option("--new-slug", default=None, help="New unique profile URL slug.")
    @click.option("--name", default=None, help="New member name.")
    @click.option(
        "--role",
        default=None,
        type=click.Choice(["alumni", "master", "phd", "pi", "postdoc", "undergrad"]),
        help="New member role.",
    )
    @click.option("--title", default=None, help="New title. Pass an empty string to clear.")
    @click.option("--email", default=None, help="New email. Pass an empty string to clear.")
    @click.option("--display-order", default=None, type=int)
    @click.option(
        "--active",
        default=None,
        type=click.Choice(["false", "true"]),
        help="Whether this member appears in public member pages.",
    )
    def update_member_command(
        slug,
        new_slug,
        name,
        role,
        title,
        email,
        display_order,
        active,
    ):
        from .services.admin_service import AdminServiceError, update_member

        try:
            member = update_member(
                slug,
                new_slug=new_slug,
                name=name,
                role=role,
                title=title,
                email=email,
                display_order=display_order,
                active=parse_cli_bool(active) if active is not None else None,
            )
        except AdminServiceError as exc:
            raise click.ClickException(str(exc)) from exc
        click.echo(format_member(member))

    @app.cli.command("list-users")
    def list_users_command():
        from .services.admin_service import list_users

        users = list_users()
        if not users:
            click.echo("No users found.")
            return
        for user in users:
            click.echo(format_user(user))

    @app.cli.command("list-members")
    def list_members_command():
        from .services.admin_service import list_members

        members = list_members()
        if not members:
            click.echo("No members found.")
            return
        for member in members:
            click.echo(format_member(member))


def parse_cli_bool(value):
    return value == "true"


def format_user(user):
    return (
        f"user id={user.id} campus_id={user.campus_id} name={user.name} "
        f"email={user.email or '-'} role={user.role}"
    )


def format_member(member):
    return (
        f"member id={member.id} campus_id={member.campus_id} slug={member.slug} "
        f"name={member.name} role={member.role} title={member.title or '-'} "
        f"email={member.email or '-'} active={member.active} "
        f"display_order={member.display_order} user_campus_id={member.user.campus_id}"
    )


def register_error_handlers(app):
    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(error):
        return jsonify({"error": "Uploaded file must be 20 MB or smaller"}), 413
