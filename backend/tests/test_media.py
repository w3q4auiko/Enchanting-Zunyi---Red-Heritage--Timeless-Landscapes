"""图片上传边界与访问控制测试。"""

import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from flask import Flask
from PIL import Image

from routes.media import bp as media_bp
from utils.auth_helper import generate_access_token


def create_test_app(upload_root: str) -> Flask:
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key-with-sufficient-length",
        JWT_ACCESS_MINUTES=30,
        JWT_ISSUER="test-issuer",
        JWT_AUDIENCE="test-audience",
        MAX_CONTENT_LENGTH=8 * 1024 * 1024,
        MAX_IMAGE_UPLOAD_BYTES=5 * 1024 * 1024,
        UPLOAD_ROOT=upload_root,
    )
    app.register_blueprint(media_bp)
    return app


class MediaUploadTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.app = create_test_app(self.temp_dir.name)
        self.client = self.app.test_client()
        self.active_user = patch("utils.auth_helper.query_one", return_value={"id": 7})
        self.active_user.start()
        with self.app.app_context():
            self.public_token = generate_access_token(7, "visitor", "public")

    def tearDown(self):
        self.active_user.stop()
        self.temp_dir.cleanup()

    def _headers(self):
        return {"Authorization": f"Bearer {self.public_token}"}

    @staticmethod
    def _png_file():
        content = io.BytesIO()
        Image.new("RGB", (8, 6), "#a61f2d").save(content, format="PNG")
        content.seek(0)
        return content

    def test_upload_requires_login(self):
        response = self.client.post(
            "/api/media/images",
            data={"file": (self._png_file(), "photo.png")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 401)

    def test_valid_image_is_normalized_and_publicly_readable(self):
        response = self.client.post(
            "/api/media/images",
            headers=self._headers(),
            data={
                "scope": "submission",
                "file": (self._png_file(), "游客照片.png"),
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["width"], 8)
        self.assertEqual(response.json["height"], 6)
        self.assertTrue(response.json["url"].startswith("/api/media/images/submission/"))

        relative = response.json["url"].removeprefix("/api/media/")
        self.assertTrue((Path(self.temp_dir.name) / relative).is_file())
        image_response = self.client.get(response.json["url"])
        self.assertEqual(image_response.status_code, 200)
        self.assertEqual(image_response.content_type, "image/png")
        self.assertIn("immutable", image_response.headers["Cache-Control"])
        image_response.close()

    def test_fake_image_is_rejected(self):
        response = self.client.post(
            "/api/media/images",
            headers=self._headers(),
            data={"file": (io.BytesIO(b"not-an-image"), "fake.png")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 415)
        self.assertFalse(list(Path(self.temp_dir.name).rglob("*.png")))


if __name__ == "__main__":
    unittest.main()
