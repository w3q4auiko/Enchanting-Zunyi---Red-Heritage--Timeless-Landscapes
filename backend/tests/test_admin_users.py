"""后台用户管理接口测试。"""

import unittest
from unittest.mock import MagicMock, patch

from flask import Flask

from routes.admin import bp as admin_bp
from utils.auth_helper import generate_access_token


class AdminUserEndpointTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(
            TESTING=True,
            SECRET_KEY="test-secret-key-with-sufficient-length",
            JWT_ACCESS_MINUTES=30,
            JWT_ISSUER="test-issuer",
            JWT_AUDIENCE="test-audience",
        )
        self.app.register_blueprint(admin_bp)
        with self.app.app_context():
            token = generate_access_token(1, "admin", "admin")
        self.headers = {"Authorization": f"Bearer {token}"}

    def test_list_users_combines_admin_and_public_accounts(self):
        rows = [
            {
                "id": 8,
                "username": "tourist01",
                "nickname": "游客",
                "role": "visitor",
                "account_type": "public",
                "create_time": "2026-08-29 10:00:00",
            }
        ]
        with (
            patch("utils.auth_helper.query_one", return_value={"id": 1}),
            patch("routes.admin.query_one", side_effect=[{"c": 2}, {"total": 1}]),
            patch("routes.admin.query_all", return_value=rows) as query_all,
        ):
            response = self.app.test_client().get(
                "/api/admin/users?account_type=public", headers=self.headers
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["data"][0]["account_type"], "public")
        self.assertEqual(response.json["admin_count"], 2)
        sql, params = query_all.call_args.args
        self.assertIn("FROM sys_public_user", sql)
        self.assertEqual(params[-3:], ["public", 10, 0])

    def test_delete_public_user_revokes_session_and_deletes_account(self):
        cursor = MagicMock()
        cursor.fetchone.return_value = {"id": 8}
        cursor.execute.side_effect = [None, 1, 1]
        manager = MagicMock()
        manager.__enter__.return_value = cursor

        with (
            patch("utils.auth_helper.query_one", return_value={"id": 1}),
            patch("routes.admin.DBManager", return_value=manager),
        ):
            response = self.app.test_client().delete(
                "/api/admin/users/public/8", headers=self.headers
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(cursor.execute.call_args_list[1].args[1], ("public", 8))
        self.assertEqual(
            cursor.execute.call_args_list[2].args,
            ("DELETE FROM sys_public_user WHERE id = %s", (8,)),
        )

    def test_current_admin_still_cannot_be_deleted(self):
        with patch("utils.auth_helper.query_one", return_value={"id": 1}):
            response = self.app.test_client().delete(
                "/api/admin/users/admin/1", headers=self.headers
            )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json["error"], "不能删除当前登录账号")


if __name__ == "__main__":
    unittest.main()
