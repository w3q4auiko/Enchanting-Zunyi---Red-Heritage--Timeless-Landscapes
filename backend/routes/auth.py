"""管理员认证与全站会话刷新接口。"""

import pymysql
from flask import Blueprint, current_app, g, jsonify, make_response, request
from werkzeug.security import generate_password_hash

from utils.auth_helper import admin_required, login_required
from utils.auth_service import (
    clear_refresh_cookie,
    create_login_payload,
    login_is_limited,
    password_matches,
    record_login_attempt,
    revoke_refresh_token,
    rotate_refresh_token,
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

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _validation_error(exc: ValidationError):
    return jsonify({"code": 400, "error": exc.message, "field": exc.field}), 400


def _refresh_cookie() -> str:
    return request.cookies.get(current_app.config["AUTH_COOKIE_NAME"], "")


def _is_same_origin_api_request() -> bool:
    """自定义请求头会触发跨域预检，用于阻止刷新/退出 CSRF。"""
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


@bp.route("/register", methods=["POST"])
@admin_required
def register():
    """由现有管理员创建新管理员，禁止匿名注册后台账号。"""
    data = get_json_body()
    try:
        username = validate_username(data.get("username"))
        nickname = validate_nickname(data.get("nickname"))
        password = validate_password(data.get("password"), username)
    except ValidationError as exc:
        return _validation_error(exc)

    if query_one("SELECT id FROM sys_user WHERE username = %s", (username,)):
        return jsonify({"code": 409, "error": "该管理员账号已存在", "field": "username"}), 409

    try:
        with DBManager() as cursor:
            cursor.execute(
                """
                INSERT INTO sys_user (username, password, nickname, role)
                VALUES (%s, %s, %s, 'admin')
                """,
                (username, generate_password_hash(password), nickname),
            )
    except pymysql.err.IntegrityError:
        return jsonify({"code": 409, "error": "该管理员账号已存在", "field": "username"}), 409
    except Exception:
        current_app.logger.exception("Admin account creation failed")
        return jsonify({"code": 500, "error": "管理员创建失败"}), 500
    return jsonify({"code": 201, "message": "管理员创建成功"}), 201


@bp.route("/login", methods=["POST"])
def login():
    """验证管理员账号；普通角色不能通过后台入口建立会话。"""
    try:
        username, password, persistent = validate_login_payload(get_json_body())
    except ValidationError as exc:
        return _validation_error(exc)

    if login_is_limited("admin", username):
        response = jsonify({"code": 429, "error": "尝试次数过多，请稍后再试"})
        response.headers["Retry-After"] = str(
            current_app.config["AUTH_LOGIN_WINDOW_MINUTES"] * 60
        )
        return response, 429

    user = query_one(
        """
        SELECT id, username, nickname, avatar, role, password
        FROM sys_user WHERE username = %s AND role = 'admin'
        """,
        (username,),
    )
    valid = password_matches(user, password)
    record_login_attempt("admin", username, valid)
    if not valid:
        return jsonify({"code": 401, "error": "账号或密码错误"}), 401

    payload, refresh_token = create_login_payload(user, "admin", persistent)
    response = make_response(jsonify(payload))
    set_refresh_cookie(response, refresh_token, persistent)
    return response


@bp.route("/refresh", methods=["POST"])
def refresh():
    """轮换刷新令牌并签发新的短期访问令牌。"""
    if not _is_same_origin_api_request():
        return jsonify({"code": 403, "error": "请求来源校验失败"}), 403
    rotated = rotate_refresh_token(_refresh_cookie())
    if not rotated:
        response = make_response(jsonify({"code": 401, "error": "会话已失效，请重新登录"}), 401)
        clear_refresh_cookie(response)
        return response

    payload, refresh_token, persistent = rotated
    response = make_response(jsonify(payload))
    set_refresh_cookie(response, refresh_token, persistent)
    return response


@bp.route("/logout", methods=["POST"])
def logout():
    """撤销当前刷新会话并清除浏览器 Cookie。"""
    if not _is_same_origin_api_request():
        return jsonify({"code": 403, "error": "请求来源校验失败"}), 403
    revoke_refresh_token(_refresh_cookie())
    response = make_response(jsonify({"code": 200, "message": "已安全退出"}))
    clear_refresh_cookie(response)
    return response


@bp.route("/me", methods=["GET"])
@login_required
def get_current_user_info():
    """返回当前管理员资料。"""
    if getattr(g, "current_account_type", None) != "admin":
        return jsonify({"code": 403, "error": "账号类型无权访问后台"}), 403

    user = query_one(
        """
        SELECT id, username, nickname, role, avatar
        FROM sys_user WHERE id = %s AND role = 'admin'
        """,
        (g.current_user_id,),
    )
    if not user:
        return jsonify({"code": 404, "error": "管理员不存在"}), 404
    user["accountType"] = "admin"
    return jsonify({"code": 200, "user": user})
