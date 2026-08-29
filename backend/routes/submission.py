"""用户内容提报模块。

该模块提供游客与用户的内容提交入口，并以审核状态驱动内容治理流程，
用于补充旅游信息系统的景区、美食与路线数据来源。
"""

from urllib.parse import urlsplit

from flask import Blueprint, current_app, g, jsonify

from utils.auth_helper import login_required
from utils.database import DBManager
from utils.request_data import get_json_body

bp = Blueprint("submission", __name__, url_prefix="/api/submission")


def _clean_text(data: dict, key: str, max_length: int) -> str:
    """将投稿字段规范化为受控长度的文本。"""
    value = data.get(key, "")
    if not isinstance(value, str):
        raise ValueError(f"{key} 格式不正确")
    value = value.strip()
    if len(value) > max_length:
        raise ValueError(f"{key} 内容过长")
    return value


def _valid_image_url(value: str) -> bool:
    """仅允许站内路径或 HTTP(S) 图片地址。"""
    if not value:
        return True
    if value.startswith("/") and not value.startswith("//"):
        return True
    parsed = urlsplit(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


@bp.route("/add", methods=["POST"])
@login_required
def submit_content():
    """内容提报入口接口。

    根据投稿类型将用户提交内容写入待审核实体，以状态标识进入内容治理
    流程，支撑旅游资源数据的持续更新。

    Args:
        None.

    Returns:
        Response: 投稿提交结果的 JSON 响应。
    """
    if getattr(g, "current_account_type", None) != "public":
        return jsonify({"code": 403, "error": "仅公众用户可以投稿"}), 403
    user_id = g.current_user_id

    data = get_json_body()
    try:
        submission_type = _clean_text(data, "type", 20)
        title = _clean_text(data, "title", 100)
        description = _clean_text(data, "desc", 10_000)
        address = _clean_text(data, "address", 255)
        image_url = _clean_text(data, "image", 255)
        price = _clean_text(data, "price", 50)
        extra = _clean_text(data, "extra", 500)
    except ValueError as exc:
        return jsonify({"code": 400, "error": f"提交失败：{exc}"}), 400

    if len(title) < 2:
        return jsonify({"code": 400, "error": "提交失败：标题至少需要 2 个字符"}), 400
    if len(description) < 10:
        return jsonify({"code": 400, "error": "提交失败：描述至少需要 10 个字符"}), 400
    if submission_type in {"scenery", "food"} and not address:
        return jsonify({"code": 400, "error": "提交失败：请填写详细地址"}), 400
    if not _valid_image_url(image_url):
        return jsonify({"code": 400, "error": "提交失败：图片地址仅支持站内路径或 HTTP(S) URL"}), 400

    sql = ""
    params = ()

    if submission_type == "scenery":
        sql = """
            INSERT INTO sys_attraction
                (category, title, description, image_url, address,
                 submitted_by, submitted_at, status)
            VALUES ('用户投稿', %s, %s, %s, %s, %s, UTC_TIMESTAMP(), 0)
        """
        params = (title, description, image_url, address, user_id)
    elif submission_type == "food":
        sql = """
            INSERT INTO sys_food
                (category, name, description, image_url, address, price,
                 submitted_by, submitted_at, status)
            VALUES ('用户投稿', %s, %s, %s, %s, %s, %s, UTC_TIMESTAMP(), 0)
        """
        params = (
            title,
            description,
            image_url,
            address,
            price,
            user_id,
        )
    elif submission_type == "route":
        sql = """
            INSERT INTO sys_route
                (category, title, description, image_url, tips,
                 submitted_by, submitted_at, status)
            VALUES ('用户投稿', %s, %s, %s, %s, %s, UTC_TIMESTAMP(), 0)
        """
        params = (title, description, image_url, extra, user_id)
    else:
        return jsonify({"error": "提交失败：不支持的投稿类型"}), 400

    try:
        with DBManager() as cursor:
            cursor.execute(sql, params)
        return jsonify({"code": 201, "msg": "投稿提交成功，请等待管理员审核。"}), 201
    except Exception:
        current_app.logger.exception("Content submission failed")
        return jsonify({"code": 500, "error": "投稿服务暂不可用，请稍后重试"}), 500
