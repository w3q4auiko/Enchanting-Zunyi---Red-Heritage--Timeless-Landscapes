"""图片媒体上传与访问接口。

用户和管理员可通过受保护的上传接口提交本地图片，服务端完成
真实类型校验、像素限制和重编码，再返回可持久化保存的站内 URL。
"""

import datetime
import os
import uuid
from pathlib import Path

from flask import Blueprint, current_app, g, jsonify, request, send_from_directory
from PIL import Image, ImageOps, UnidentifiedImageError

from utils.auth_helper import login_required

bp = Blueprint("media", __name__, url_prefix="/api/media")

_ALLOWED_SCOPES = {
    "submission",
    "attraction",
    "food",
    "food-street",
    "region",
    "route",
    "other",
}
_FORMAT_CONFIG = {
    "JPEG": ("jpg", {"format": "JPEG", "quality": 88, "optimize": True}),
    "PNG": ("png", {"format": "PNG", "optimize": True}),
    "WEBP": ("webp", {"format": "WEBP", "quality": 86, "method": 6}),
}
_MAX_PIXELS = 40_000_000
_MAX_EDGE = 12_000


def _upload_root() -> Path:
    """返回并确保媒体存储根目录存在。"""
    root = Path(current_app.config["UPLOAD_ROOT"]).resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def _file_size(stream) -> int:
    """不消费文件流地获取上传字节数。"""
    current = stream.tell()
    stream.seek(0, os.SEEK_END)
    size = stream.tell()
    stream.seek(current)
    return size


@bp.post("/images")
@login_required
def upload_image():
    """校验、标准化并保存单张图片。"""
    if getattr(g, "current_account_type", None) not in {"public", "admin"}:
        return jsonify({"code": 403, "error": "当前账号无上传权限"}), 403

    uploaded = request.files.get("file")
    if not uploaded or not uploaded.filename:
        return jsonify({"code": 400, "error": "请选择需要上传的图片"}), 400

    size = _file_size(uploaded.stream)
    max_bytes = current_app.config["MAX_IMAGE_UPLOAD_BYTES"]
    if size <= 0:
        return jsonify({"code": 400, "error": "上传的图片为空文件"}), 400
    if size > max_bytes:
        max_mb = max_bytes // (1024 * 1024)
        return jsonify({"code": 413, "error": f"图片不能超过 {max_mb}MB"}), 413

    temporary = None
    try:
        uploaded.stream.seek(0)
        with Image.open(uploaded.stream) as probe:
            image_format = (probe.format or "").upper()
            width, height = probe.size
            probe.verify()

        if image_format not in _FORMAT_CONFIG:
            return jsonify({"code": 415, "error": "仅支持 JPG、PNG 或 WebP 图片"}), 415
        if width <= 0 or height <= 0 or width > _MAX_EDGE or height > _MAX_EDGE:
            return jsonify({"code": 400, "error": "图片尺寸超出允许范围"}), 400
        if width * height > _MAX_PIXELS:
            return jsonify({"code": 400, "error": "图片像素过高，请压缩后重试"}), 400

        extension, save_options = _FORMAT_CONFIG[image_format]
        scope = request.form.get("scope", "other").strip().lower()
        if scope not in _ALLOWED_SCOPES:
            scope = "other"

        today = datetime.datetime.now(datetime.timezone.utc)
        relative_dir = Path("images") / scope / f"{today:%Y}" / f"{today:%m}"
        target_dir = _upload_root() / relative_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid.uuid4().hex}.{extension}"
        target = target_dir / filename
        temporary = target.with_suffix(target.suffix + ".tmp")

        uploaded.stream.seek(0)
        with Image.open(uploaded.stream) as source:
            normalized = ImageOps.exif_transpose(source)
            if image_format == "JPEG" and normalized.mode not in {"RGB", "L"}:
                normalized = normalized.convert("RGB")
            elif image_format in {"PNG", "WEBP"} and normalized.mode not in {
                "RGB",
                "RGBA",
                "L",
                "LA",
            }:
                normalized = normalized.convert("RGBA" if "transparency" in normalized.info else "RGB")
            normalized.save(temporary, **save_options)
        temporary.replace(target)
    except (Image.DecompressionBombError, UnidentifiedImageError, OSError, ValueError):
        current_app.logger.info("Rejected invalid image upload", exc_info=True)
        return jsonify({"code": 415, "error": "图片文件损坏或格式不受支持"}), 415
    except Exception:
        current_app.logger.exception("Image upload failed")
        return jsonify({"code": 500, "error": "图片上传失败，请稍后重试"}), 500
    finally:
        # 重编码中断时不在存储目录遗留半成品。
        if temporary and temporary.exists():
            temporary.unlink()

    relative_url = "/".join((*relative_dir.parts, filename))
    return jsonify(
        {
            "code": 201,
            "message": "图片上传成功",
            "url": f"/api/media/{relative_url}",
            "width": width,
            "height": height,
            "size": target.stat().st_size,
        }
    ), 201


@bp.get("/images/<path:filename>")
def serve_image(filename: str):
    """输出已上传图片，随机文件名允许长时间公开缓存。"""
    response = send_from_directory(_upload_root() / "images", filename, conditional=True)
    response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response
