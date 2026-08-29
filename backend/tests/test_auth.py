"""认证输入、令牌声明和接口边界测试。"""

import unittest
from unittest.mock import patch

import jwt
from flask import Flask, jsonify
from werkzeug.security import generate_password_hash

from routes.auth import bp as auth_bp
from routes.public_auth import bp as public_auth_bp
from utils.auth_helper import admin_required, generate_access_token, login_required
from utils.auth_validation import (
    ValidationError,
    normalize_login_username,
    validate_password,
    validate_username,
)


def create_test_app() -> Flask:
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key-with-sufficient-length",
        JWT_ACCESS_MINUTES=30,
        JWT_ISSUER="test-issuer",
        JWT_AUDIENCE="test-audience",
        AUTH_LOGIN_WINDOW_MINUTES=15,
        AUTH_REFRESH_DAYS=30,
        AUTH_COOKIE_NAME="test_refresh",
        AUTH_COOKIE_SECURE=False,
        AUTH_COOKIE_SAMESITE="Lax",
    )
    app.register_blueprint(auth_bp)
    app.register_blueprint(public_auth_bp)

    @app.route("/protected")
    @login_required
    def protected():
        return jsonify({"ok": True})

    @app.route("/admin-protected")
    @admin_required
    def admin_protected():
        return jsonify({"ok": True})

    return app


class ValidationTests(unittest.TestCase):
    def test_username_is_normalized(self):
        self.assertEqual(validate_username("  Tourist_01 "), "tourist_01")

    def test_username_rejects_invalid_characters(self):
        with self.assertRaises(ValidationError):
            validate_username("张三")

    def test_login_keeps_legacy_username_compatible(self):
        self.assertEqual(normalize_login_username("  老用户  "), "老用户")

    def test_password_requires_three_character_groups(self):
        with self.assertRaises(ValidationError):
            validate_password("onlyletters", "tourist")
        self.assertEqual(validate_password("SafePass9!", "tourist"), "SafePass9!")


class TokenTests(unittest.TestCase):
    def setUp(self):
        self.app = create_test_app()

    def test_access_token_contains_security_claims(self):
        with self.app.app_context():
            token = generate_access_token(7, "visitor", "public")
            payload = jwt.decode(
                token,
                self.app.config["SECRET_KEY"],
                algorithms=["HS256"],
                issuer="test-issuer",
                audience="test-audience",
            )
        self.assertEqual(payload["sub"], "7")
        self.assertEqual(payload["token_type"], "access")
        self.assertEqual(payload["account_type"], "public")
        self.assertTrue(payload["jti"])

    def test_protected_route_rejects_token_without_required_claims(self):
        legacy_token = jwt.encode(
            {"sub": "1", "role": "admin"},
            self.app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        response = self.app.test_client().get(
            "/protected", headers={"Authorization": f"Bearer {legacy_token}"}
        )
        self.assertEqual(response.status_code, 401)

    def test_deleted_admin_token_is_rejected_immediately(self):
        with self.app.app_context():
            token = generate_access_token(99, "admin", "admin")
        with patch("utils.auth_helper.query_one", return_value=None):
            response = self.app.test_client().get(
                "/admin-protected", headers={"Authorization": f"Bearer {token}"}
            )
        self.assertEqual(response.status_code, 401)

    def test_deleted_public_user_token_is_rejected_immediately(self):
        with self.app.app_context():
            token = generate_access_token(88, "visitor", "public")
        with patch("utils.auth_helper.query_one", return_value=None):
            response = self.app.test_client().get(
                "/protected", headers={"Authorization": f"Bearer {token}"}
            )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["error"], "账号已失效，请重新登录")

    def test_active_public_user_token_is_accepted(self):
        with self.app.app_context():
            token = generate_access_token(7, "visitor", "public")
        with patch("utils.auth_helper.query_one", return_value={"id": 7}):
            response = self.app.test_client().get(
                "/protected", headers={"Authorization": f"Bearer {token}"}
            )
        self.assertEqual(response.status_code, 200)


class AuthEndpointTests(unittest.TestCase):
    def setUp(self):
        self.app = create_test_app()
        self.client = self.app.test_client()

    def test_public_registration_validates_before_database_access(self):
        with patch("routes.public_auth.query_one") as query:
            response = self.client.post(
                "/api/public/register",
                json={"username": "bad name", "nickname": "游客", "password": "SafePass9!"},
            )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["field"], "username")
        query.assert_not_called()

    def test_public_login_uses_generic_credential_error(self):
        with (
            patch("routes.public_auth.login_is_limited", return_value=False),
            patch("routes.public_auth.query_one", return_value=None),
            patch("routes.public_auth.record_login_attempt") as record,
        ):
            response = self.client.post(
                "/api/public/login",
                json={"username": "tourist01", "password": "WrongPass9!"},
            )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["error"], "账号或密码错误")
        record.assert_called_once_with("public", "tourist01", False)

    def test_admin_registration_is_not_public(self):
        response = self.client.post(
            "/api/auth/register",
            json={"username": "newadmin", "nickname": "管理员", "password": "SafePass9!"},
        )
        self.assertEqual(response.status_code, 401)

    def test_successful_public_login_sets_http_only_refresh_cookie(self):
        user = {
            "id": 8,
            "username": "tourist01",
            "nickname": "游客",
            "avatar": None,
            "password": generate_password_hash("SafePass9!"),
        }
        payload = {
            "code": 200,
            "accessToken": "short-lived-token",
            "persistent": False,
            "user": {"id": 8, "accountType": "public"},
        }
        with (
            patch("routes.public_auth.login_is_limited", return_value=False),
            patch("routes.public_auth.query_one", return_value=user),
            patch("routes.public_auth.record_login_attempt"),
            patch("routes.public_auth.create_login_payload", return_value=(payload, "refresh-value")),
        ):
            response = self.client.post(
                "/api/public/login",
                json={"username": "tourist01", "password": "SafePass9!", "remember": False},
            )
        cookie = response.headers["Set-Cookie"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["accessToken"], "short-lived-token")
        self.assertIn("HttpOnly", cookie)
        self.assertIn("Path=/api/auth", cookie)
        self.assertIn("SameSite=Lax", cookie)

    def test_admin_token_cannot_read_public_profile(self):
        with self.app.app_context():
            token = generate_access_token(1, "admin", "admin")
        with (
            patch("utils.auth_helper.query_one", return_value={"id": 1}),
            patch("routes.public_auth.query_one") as query,
        ):
            response = self.client.get(
                "/api/public/info",
                headers={"Authorization": f"Bearer {token}"},
            )
        self.assertEqual(response.status_code, 403)
        query.assert_not_called()

    def test_missing_refresh_cookie_returns_401_and_clears_cookie(self):
        with patch("routes.auth.rotate_refresh_token", return_value=None):
            response = self.client.post(
                "/api/auth/refresh", headers={"X-Requested-With": "XMLHttpRequest"}
            )
        self.assertEqual(response.status_code, 401)
        self.assertIn("test_refresh=", response.headers["Set-Cookie"])

    def test_refresh_rejects_request_without_csrf_header(self):
        response = self.client.post("/api/auth/refresh")
        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
