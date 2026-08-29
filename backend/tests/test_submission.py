"""用户投稿输入校验、权限和审计字段测试。"""

import unittest
from unittest.mock import patch

from flask import Flask

from routes.submission import bp as submission_bp
from utils.auth_helper import generate_access_token


def create_test_app() -> Flask:
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key-with-sufficient-length",
        JWT_ACCESS_MINUTES=30,
        JWT_ISSUER="test-issuer",
        JWT_AUDIENCE="test-audience",
    )
    app.register_blueprint(submission_bp)
    return app


class SubmissionTests(unittest.TestCase):
    def setUp(self):
        self.app = create_test_app()
        self.client = self.app.test_client()
        self.active_user = patch("utils.auth_helper.query_one", return_value={"id": 12})
        self.active_user.start()
        with self.app.app_context():
            self.public_token = generate_access_token(12, "visitor", "public")
            self.admin_token = generate_access_token(1, "admin", "admin")

    def tearDown(self):
        self.active_user.stop()

    def _headers(self, token=None):
        return {"Authorization": f"Bearer {token or self.public_token}"}

    def test_only_public_accounts_can_submit(self):
        response = self.client.post(
            "/api/submission/add",
            headers=self._headers(self.admin_token),
            json={"type": "route", "title": "测试路线", "desc": "这是一段足够详细的路线介绍。"},
        )
        self.assertEqual(response.status_code, 403)

    def test_scenery_requires_address_on_server(self):
        with patch("routes.submission.DBManager") as manager:
            response = self.client.post(
                "/api/submission/add",
                headers=self._headers(),
                json={"type": "scenery", "title": "测试景点", "desc": "这是一段足够详细的景点介绍。"},
            )
        self.assertEqual(response.status_code, 400)
        manager.assert_not_called()

    def test_unsafe_image_scheme_is_rejected(self):
        response = self.client.post(
            "/api/submission/add",
            headers=self._headers(),
            json={
                "type": "route",
                "title": "测试路线",
                "desc": "这是一段足够详细的路线介绍。",
                "image": "javascript:alert(1)",
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_route_submission_records_submitter_and_pending_status(self):
        with patch("routes.submission.DBManager") as manager:
            cursor = manager.return_value.__enter__.return_value
            response = self.client.post(
                "/api/submission/add",
                headers=self._headers(),
                json={
                    "type": "route",
                    "title": "娄山关徒步线",
                    "desc": "从游客中心出发，沿山脊完成徒步环线。",
                    "extra": "全程 8 公里，建议 3 小时",
                    "image": "/api/media/images/submission/2026/08/demo.webp",
                },
            )

        self.assertEqual(response.status_code, 201)
        sql, params = cursor.execute.call_args.args
        self.assertIn("submitted_by", sql)
        self.assertIn("status", sql)
        self.assertEqual(params[-1], 12)


if __name__ == "__main__":
    unittest.main()
