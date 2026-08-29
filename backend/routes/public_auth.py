"""公众账号注册、登录和资料接口。"""

import pymysql
from flask import Blueprint, current_app, g, jsonify, make_response
from werkzeug.security import generate_password_hash

from utils.auth_helper import login_required
from utils.auth_service import (
    create_login_payload,
    login_is_limited,
    password_matches,
    record_login_attempt,
    record_registration_attempt,
    registration_is_limited,
    set_refresh_cookie,
)
from utils.auth_validation import (
    ValidationError,
    validate_login_payload,
    validate_nickname,
    validate_password,
    validate_username,
)
from utils.database import DBManager, query_one
from utils.request_data import get_json_body

bp = Blueprint("public_auth", __name__, url_prefix="/api/public")


def _validation_error(exc: ValidationError):
    return jsonify({"code": 400, "error": exc.message, "field": exc.field}), 400


@bp.route("/register", methods=["POST"])
def register():
    """创建公众账号；所有安全规则均由服务端再次校验。"""
    data = get_json_body()
    try:
        username = validate_username(data.get("username"))
        nickname = validate_nickname(data.get("nickname"))
        password = validate_password(data.get("password"), username)
    except ValidationError as exc:
        return _validation_error(exc)

    if registration_is_limited():
        response = jsonify({"code": 429, "error": "注册请求过于频繁，请一小时后再试"})
        response.headers["Retry-After"] = "3600"
        return response, 429

    if query_one("SELECT id FROM sys_public_user WHERE username = %s", (username,)):
        return jsonify({"code": 409, "error": "该账号已被注册", "field": "username"}), 409

    record_registration_attempt(username)

    try:
        with DBManager() as cursor:
            cursor.execute(
                """
                INSERT INTO sys_public_user (username, password, nickname)
                VALUES (%s, %s, %s)
                """,
                (username, generate_password_hash(password), nickname),
            )
    except pymysql.err.IntegrityError:
        # 唯一索引是并发注册下的最终防线。
        return jsonify({"code": 409, "error": "该账号已被注册", "field": "username"}), 409
    except Exception:
        current_app.logger.exception("Public account registration failed")
        return jsonify({"code": 500, "error": "注册服务暂不可用，请稍后重试"}), 500

    return jsonify({"code": 201, "message": "注册成功，请登录", "username": username}), 201


@bp.route("/login", methods=["POST"])
def login():
    """验证公众账号并签发短期访问令牌和 HttpOnly 刷新令牌。"""
    try:
        username, password, persistent = validate_login_payload(get_json_body())
    except ValidationError as exc:
        return _validation_error(exc)

    if login_is_limited("public", username):
        response = jsonify({"code": 429, "error": "尝试次数过多，请稍后再试"})
        response.headers["Retry-After"] = str(
            current_app.config["AUTH_LOGIN_WINDOW_MINUTES"] * 60
        )
        return response, 429

    user = query_one(
        """
        SELECT id, username, nickname, avatar, password
        FROM sys_public_user WHERE username = %s
        """,
        (username,),
    )
    valid = password_matches(user, password)
    record_login_attempt("public", username, valid)
    if not valid:
        # 不区分账号不存在或密码错误，防止账号枚举。
        return jsonify({"code": 401, "error": "账号或密码错误"}), 401

    payload, refresh_token = create_login_payload(user, "public", persistent)
    response = make_response(jsonify(payload))
    set_refresh_cookie(response, refresh_token, persistent)
    return response


@bp.route("/info", methods=["GET"])
@login_required
def user_info():
    """返回当前公众账号信息，并阻止管理员令牌跨账号域访问。"""
    if getattr(g, "current_account_type", None) != "public":
        return jsonify({"code": 403, "error": "账号类型无权访问该资源"}), 403

    user = query_one(
        "SELECT id, username, nickname, avatar FROM sys_public_user WHERE id = %s",
        (g.current_user_id,),
    )
    if not user:
        return jsonify({"code": 404, "error": "用户不存在"}), 404
    user["role"] = "visitor"
    user["accountType"] = "public"
    return jsonify({"code": 200, "user": user})
