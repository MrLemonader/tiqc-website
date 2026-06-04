import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from app import create_app
from app.extensions import db
from app.models import Member
from app.services.admin_service import (
    AdminServiceError,
    create_member,
    create_user,
    update_member,
)
from config import Config


class AdminServiceTestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class AdminServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory(ignore_cleanup_errors=True)
        temp_path = Path(self.temp_dir.name)
        AdminServiceTestConfig.UPLOAD_FOLDER = str(temp_path / "uploads")
        AdminServiceTestConfig.AVATAR_UPLOAD_FOLDER = str(temp_path / "uploads" / "avatars")
        AdminServiceTestConfig.FRONTEND_DIST_FOLDER = str(temp_path / "frontend" / "dist")
        self.app = create_app(AdminServiceTestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        self.temp_dir.cleanup()

    def test_create_user_and_member(self):
        user = create_user("20249901", "Test Member", "test@example.edu")
        member = create_member(
            user_campus_id="20249901",
            slug="test-member",
            role="phd",
            title="PhD Student",
            display_order=30,
        )

        self.assertEqual(user.role, "member")
        self.assertEqual(member.user_id, user.id)
        self.assertEqual(member.name, "Test Member")
        self.assertEqual(member.email, "test@example.edu")
        self.assertTrue(member.active)

    def test_create_admin_user(self):
        user = create_user("admin-test", "Admin User", role="admin")

        self.assertEqual(user.role, "admin")

    def test_rejects_duplicate_user_campus_id(self):
        create_user("20249901", "Test Member")

        with self.assertRaisesRegex(AdminServiceError, "already exists"):
            create_user("20249901", "Duplicate")

    def test_rejects_duplicate_member_binding_and_slug(self):
        create_user("20249901", "Test Member")
        create_user("20249902", "Second Member")
        create_member("20249901", "test-member", "phd")

        with self.assertRaisesRegex(AdminServiceError, "already has"):
            create_member("20249901", "duplicate-binding", "phd")
        with self.assertRaisesRegex(AdminServiceError, "slug already exists"):
            create_member("20249902", "test-member", "postdoc")

    def test_rejects_invalid_roles(self):
        with self.assertRaisesRegex(AdminServiceError, "must be one of"):
            create_user("bad-role", "Bad Role", role="owner")

        create_user("20249901", "Test Member")
        with self.assertRaisesRegex(AdminServiceError, "must be one of"):
            create_member("20249901", "test-member", "visitor")

    def test_update_member_admin_fields(self):
        create_user("20249901", "Test Member", "test@example.edu")
        create_member("20249901", "test-member", "phd")

        member = update_member(
            "test-member",
            new_slug="test-member-updated",
            name="Updated Name",
            role="postdoc",
            title="Updated Title",
            email="updated@example.edu",
            active=False,
            display_order=5,
        )

        self.assertEqual(member.slug, "test-member-updated")
        self.assertEqual(member.name, "Updated Name")
        self.assertEqual(member.role, "postdoc")
        self.assertEqual(member.title, "Updated Title")
        self.assertEqual(member.email, "updated@example.edu")
        self.assertFalse(member.active)
        self.assertEqual(member.display_order, 5)
        self.assertEqual(Member.query.filter_by(active=True).all(), [])


class AdminCliTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory(ignore_cleanup_errors=True)
        temp_path = Path(self.temp_dir.name)
        AdminServiceTestConfig.UPLOAD_FOLDER = str(temp_path / "uploads")
        AdminServiceTestConfig.AVATAR_UPLOAD_FOLDER = str(temp_path / "uploads" / "avatars")
        AdminServiceTestConfig.FRONTEND_DIST_FOLDER = str(temp_path / "frontend" / "dist")
        self.app = create_app(AdminServiceTestConfig)
        self.runner = self.app.test_cli_runner()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        self.temp_dir.cleanup()

    def test_cli_create_list_and_update(self):
        result = self.runner.invoke(
            args=[
                "create-user",
                "--campus-id",
                "20249903",
                "--name",
                "CLI Member",
                "--email",
                "cli@example.edu",
            ]
        )
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("campus_id=20249903", result.output)

        result = self.runner.invoke(
            args=[
                "create-member",
                "--user-campus-id",
                "20249903",
                "--slug",
                "cli-member",
                "--role",
                "phd",
                "--title",
                "PhD Student",
                "--display-order",
                "40",
                "--active",
                "true",
            ]
        )
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("slug=cli-member", result.output)

        result = self.runner.invoke(args=["list-users"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("CLI Member", result.output)

        result = self.runner.invoke(args=["list-members"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("cli-member", result.output)

        result = self.runner.invoke(
            args=[
                "update-member",
                "--slug",
                "cli-member",
                "--new-slug",
                "cli-member-updated",
                "--active",
                "false",
                "--display-order",
                "12",
            ]
        )
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("slug=cli-member-updated", result.output)
        self.assertIn("active=False", result.output)

    def test_cli_reports_duplicate_user(self):
        self.runner.invoke(args=["create-user", "--campus-id", "20249903", "--name", "User"])
        result = self.runner.invoke(
            args=["create-user", "--campus-id", "20249903", "--name", "Duplicate"]
        )

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("already exists", result.output)


if __name__ == "__main__":
    unittest.main()
