"""登录限流、刷新令牌轮换与认证响应组装。"""

import datetime
import hashlib
import hmac
import secrets

from flask import current_app, request
from werkzeug.security import check_password_hash, generate_password_hash

from utils.auth_helper import generate_access_token
from utils.database import DBManager, execute, query_one

# 即使账号不存在也执行一次等价哈希校验，降低通过响应耗时枚举账号的风险。
_DUMMY_PASSWORD_HASH = generate_password_hash("dummy-password-for-timing-only")


def _utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


def _client_ip() -> str:
    return (request.remote_addr or "unknown")[:45]


def _identity_hash(username: str) -> str:
    secret = current_app.config["SECRET_KEY"].encode("utf-8")
    normalized = username.casefold().encode("utf-8")
    return hmac.new(secret, normalized, hashlib.sha256).hexdigest()


def login_is_limited(account_type: str, username: str) -> bool:
    """判断同一账号和来源地址在窗口内是否超过失败上限。"""
    window = current_app.config["AUTH_LOGIN_WINDOW_MINUTES"]
    cutoff = _utcnow() - datetime.timedelta(minutes=window)
    row = query_one(
        """
        SELECT COUNT(*) AS failures
        FROM sys_auth_login_attempt
        WHERE event_type = 'login' AND account_type = %s
          AND identity_hash = %s AND ip_address = %s
          AND success = 0 AND created_at >= %s
        """,
        (account_type, _identity_hash(username), _client_ip(), cutoff),
    )
    return (row or {}).get("failures", 0) >= current_app.config["AUTH_LOGIN_MAX_FAILURES"]


def record_login_attempt(account_type: str, username: str, success: bool) -> None:
    """记录认证结果；成功后清理同一主体此前的失败记录。"""
    identity_hash = _identity_hash(username)
    ip_address = _client_ip()
    execute(
        """
        INSERT INTO sys_auth_login_attempt
            (event_type, account_type, identity_hash, ip_address, success)
        VALUES ('login', %s, %s, %s, %s)
        """,
        (account_type, identity_hash, ip_address, int(success)),
    )
    if success:
        execute(
            """
            DELETE FROM sys_auth_login_attempt
            WHERE event_type = 'login' AND account_type = %s
              AND identity_hash = %s AND ip_address = %s
              AND success = 0
            """,
            (account_type, identity_hash, ip_address),
        )
        if secrets.randbelow(100) == 0:
            _cleanup_expired_auth_records()


def _cleanup_expired_auth_records() -> None:
    """低频、分批清理认证历史，避免安全表无限增长。"""
    try:
        execute(
            """
            DELETE FROM sys_auth_login_attempt
            WHERE created_at < UTC_TIMESTAMP() - INTERVAL 7 DAY
            LIMIT 1000
            """
        )
        execute(
            """
            DELETE FROM sys_auth_refresh_token
            WHERE expires_at < UTC_TIMESTAMP() - INTERVAL 7 DAY
               OR revoked_at < UTC_TIMESTAMP() - INTERVAL 7 DAY
            LIMIT 1000
            """
        )
    except Exception:
        # 清理失败不能中断用户登录，后续请求仍会再次尝试。
        current_app.logger.warning("Auth history cleanup failed", exc_info=True)


def registration_is_limited() -> bool:
    """限制单个来源地址每小时可发起的有效注册请求数。"""
    cutoff = _utcnow() - datetime.timedelta(hours=1)
    row = query_one(
        """
        SELECT COUNT(*) AS attempts
        FROM sys_auth_login_attempt
        WHERE event_type = 'register' AND account_type = 'public'
          AND ip_address = %s AND created_at >= %s
        """,
        (_client_ip(), cutoff),
    )
    return (row or {}).get("attempts", 0) >= current_app.config["AUTH_REGISTER_MAX_PER_HOUR"]


def record_registration_attempt(username: str) -> None:
    """记录已通过字段校验的注册请求，限制密码哈希资源滥用。"""
    execute(
        """
        INSERT INTO sys_auth_login_attempt
            (event_type, account_type, identity_hash, ip_address, success)
        VALUES ('register', 'public', %s, %s, 0)
        """,
        (_identity_hash(username), _client_ip()),
    )


def password_matches(user: dict | None, password: str) -> bool:
    """以近似恒定的哈希工作量验证密码，并兼容损坏的旧哈希。"""
    password_hash = user.get("password") if user else _DUMMY_PASSWORD_HASH
    try:
        valid = check_password_hash(password_hash, password)
    except (TypeError, ValueError):
        valid = False
    return bool(user) and valid


def _hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("ascii")).hexdigest()


def _insert_refresh_token(cursor, user_id, account_type: str, persistent: bool) -> str:
    raw_token = secrets.token_urlsafe(64)
    expires_at = _utcnow() + datetime.timedelta(
        days=current_app.config["AUTH_REFRESH_DAYS"] if persistent else 1
    )
    cursor.execute(
        """
        INSERT INTO sys_auth_refresh_token
            (token_hash, user_id, account_type, persistent, expires_at, user_agent, ip_address)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            _hash_refresh_token(raw_token),
            user_id,
            account_type,
            int(persistent),
            expires_at,
            (request.user_agent.string or "")[:255],
            _client_ip(),
        ),
    )
    return raw_token


def _public_user(user: dict, account_type: str) -> dict:
    return {
        "id": user["id"],
        "username": user["username"],
        "nickname": user.get("nickname") or ("管理员" if account_type == "admin" else "游客"),
        "avatar": user.get("avatar"),
        "role": user.get("role") or ("admin" if account_type == "admin" else "visitor"),
        "accountType": account_type,
    }


def create_login_payload(user: dict, account_type: str, persistent: bool) -> tuple[dict, str]:
    """创建访问令牌与数据库持久化刷新会话。"""
    role = user.get("role") or ("admin" if account_type == "admin" else "visitor")
    access_token = generate_access_token(user["id"], role, account_type)
    with DBManager(transactional=True) as cursor:
        refresh_token = _insert_refresh_token(cursor, user["id"], account_type, persistent)
    payload = {
        "code": 200,
        "message": "登录成功",
        "accessToken": access_token,
        "expiresIn": current_app.config["JWT_ACCESS_MINUTES"] * 60,
        "persistent": persistent,
        "user": _public_user(user, account_type),
    }
    return payload, refresh_token


def rotate_refresh_token(raw_token: str) -> tuple[dict, str, bool] | None:
    """单次使用并轮换刷新令牌；并发复用只允许一个请求成功。"""
    if not raw_token:
        return None

    with DBManager(transactional=True) as cursor:
        cursor.execute(
            """
            SELECT id, user_id, account_type, persistent
            FROM sys_auth_refresh_token
            WHERE token_hash = %s AND revoked_at IS NULL AND expires_at > UTC_TIMESTAMP(6)
            FOR UPDATE
            """,
            (_hash_refresh_token(raw_token),),
        )
        session = cursor.fetchone()
        if not session:
            return None

        if session["account_type"] == "admin":
            cursor.execute(
                """
                SELECT id, username, nickname, avatar, role
                FROM sys_user WHERE id = %s AND role = 'admin'
                """,
                (session["user_id"],),
            )
        else:
            cursor.execute(
                """
                SELECT id, username, nickname, avatar
                FROM sys_public_user WHERE id = %s
                """,
                (session["user_id"],),
            )
        user = cursor.fetchone()
        if not user:
            cursor.execute(
                "UPDATE sys_auth_refresh_token SET revoked_at = UTC_TIMESTAMP(6) WHERE id = %s",
                (session["id"],),
            )
            return None

        cursor.execute(
            """
            UPDATE sys_auth_refresh_token
            SET revoked_at = UTC_TIMESTAMP(6), last_used_at = UTC_TIMESTAMP(6)
            WHERE id = %s
            """,
            (session["id"],),
        )
        persistent = bool(session["persistent"])
        new_refresh_token = _insert_refresh_token(
            cursor, user["id"], session["account_type"], persistent
        )

    role = user.get("role") or ("admin" if session["account_type"] == "admin" else "visitor")
    payload = {
        "code": 200,
        "accessToken": generate_access_token(user["id"], role, session["account_type"]),
        "expiresIn": current_app.config["JWT_ACCESS_MINUTES"] * 60,
        "persistent": persistent,
        "user": _public_user(user, session["account_type"]),
    }
    return payload, new_refresh_token, persistent


def revoke_refresh_token(raw_token: str) -> None:
    """撤销当前刷新令牌；重复退出保持幂等。"""
    if raw_token:
        execute(
            """
            UPDATE sys_auth_refresh_token
            SET revoked_at = COALESCE(revoked_at, UTC_TIMESTAMP(6))
            WHERE token_hash = %s
            """,
            (_hash_refresh_token(raw_token),),
        )


def set_refresh_cookie(response, token: str, persistent: bool) -> None:
    """写入仅服务端可读的刷新令牌 Cookie。"""
    max_age = current_app.config["AUTH_REFRESH_DAYS"] * 86400 if persistent else None
    response.set_cookie(
        current_app.config["AUTH_COOKIE_NAME"],
        token,
        max_age=max_age,
        secure=current_app.config["AUTH_COOKIE_SECURE"],
        httponly=True,
        samesite=current_app.config["AUTH_COOKIE_SAMESITE"],
        path="/api/auth",
    )


def clear_refresh_cookie(response) -> None:
    response.delete_cookie(
        current_app.config["AUTH_COOKIE_NAME"],
        secure=current_app.config["AUTH_COOKIE_SECURE"],
        httponly=True,
        samesite=current_app.config["AUTH_COOKIE_SAMESITE"],
        path="/api/auth",
    )
