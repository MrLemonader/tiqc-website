import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from app import create_app
from app.extensions import db
from app.services.admin_service import create_member, create_user
from config import Config


class AuthApiTestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    DEFAULT_CAMPUS_ID = ""


class AuthApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory(ignore_cleanup_errors=True)
        temp_path = Path(self.temp_dir.name)
        AuthApiTestConfig.UPLOAD_FOLDER = str(temp_path / "uploads")
        AuthApiTestConfig.AVATAR_UPLOAD_FOLDER = str(temp_path / "uploads" / "avatars")
        AuthApiTestConfig.FRONTEND_DIST_FOLDER = str(temp_path / "frontend" / "dist")
        self.app = create_app(AuthApiTestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        create_user("20249901", "Alice Member", "alice@example.edu")
        create_user("20249902", "Bob Member", "bob@example.edu")
        create_user("admin-test", "Admin Only", "admin@example.edu", role="admin")
        create_member("20249901", "alice-member", "phd", display_order=10)
        create_member("20249902", "bob-member", "postdoc", active=False)
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        self.temp_dir.cleanup()

    def test_visitor_can_browse_active_members_but_cannot_edit_profile(self):
        response = self.client.get("/api/members")
        self.assertEqual(response.status_code, 200)
        members = response.get_json()["members"]
        self.assertEqual([member["slug"] for member in members], ["alice-member"])

        response = self.client.get("/api/members/alice-member")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/profile")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()["error"], "login_required")

    def test_login_rejects_missing_or_unknown_campus_id(self):
        response = self.client.post("/api/login", json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "campus_id_required")

        response = self.client.post("/api/login", json={"campus_id": "20249901"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "password_required")

        response = self.client.post(
            "/api/login", json={"campus_id": "missing", "password": "missing"}
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()["error"], "invalid_credentials")

        response = self.client.post(
            "/api/login", json={"campus_id": "20249901", "password": "wrong-password"}
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()["error"], "invalid_credentials")

        response = self.client.get("/api/me")
        self.assertEqual(response.status_code, 401)

    def test_login_allows_member_to_read_and_update_own_profile(self):
        response = self.client.post(
            "/api/login", json={"campus_id": "20249901", "password": "20249901"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("campus_id=20249901", response.headers.get("Set-Cookie", ""))

        response = self.client.get("/api/me")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["user"]["campus_id"], "20249901")

        response = self.client.get("/api/profile")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["member"]["slug"], "alice-member")

        response = self.client.patch(
            "/api/profile",
            json={
                "bio": "Updated by Alice.",
                "email": "alice-updated@example.edu",
                "name": "Forbidden Name",
            },
        )
        self.assertEqual(response.status_code, 200)
        member = response.get_json()["member"]
        self.assertEqual(member["bio"], "Updated by Alice.")
        self.assertEqual(member["email"], "alice-updated@example.edu")
        self.assertEqual(member["name"], "Alice Member")

    def test_logout_clears_login_cookie(self):
        self.client.post(
            "/api/login", json={"campus_id": "20249901", "password": "20249901"}
        )

        response = self.client.post("/api/logout")
        self.assertEqual(response.status_code, 200)
        self.assertIn("campus_id=", response.headers.get("Set-Cookie", ""))

        response = self.client.get("/api/me")
        self.assertEqual(response.status_code, 401)

    def test_logged_in_user_without_member_gets_profile_error(self):
        response = self.client.post(
            "/api/login", json={"campus_id": "admin-test", "password": "admin-test"}
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/profile")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error"], "member_profile_not_found")

    def test_change_password_requires_login_and_valid_current_password(self):
        response = self.client.post(
            "/api/password",
            json={"current_password": "20249901", "new_password": "new-password"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()["error"], "login_required")

        self.client.post(
            "/api/login", json={"campus_id": "20249901", "password": "20249901"}
        )

        response = self.client.post(
            "/api/password",
            json={"current_password": "wrong-password", "new_password": "new-password"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()["error"], "invalid_current_password")

        response = self.client.post(
            "/api/password",
            json={"current_password": "20249901", "new_password": "short"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "new_password_too_short")

    def test_change_password_replaces_login_password(self):
        response = self.client.post(
            "/api/login", json={"campus_id": "20249901", "password": "20249901"}
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/api/password",
            json={"current_password": "20249901", "new_password": "updated-password"},
        )
        self.assertEqual(response.status_code, 200)
        self.client.post("/api/logout")

        response = self.client.post(
            "/api/login", json={"campus_id": "20249901", "password": "20249901"}
        )
        self.assertEqual(response.status_code, 401)

        response = self.client.post(
            "/api/login", json={"campus_id": "20249901", "password": "updated-password"}
        )
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
