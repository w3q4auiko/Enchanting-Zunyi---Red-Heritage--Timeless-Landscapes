"""身份认证与授权基础设施模块。

该模块提供基于 JWT 的无状态认证与角色鉴权能力，作为旅游信息系统
各业务域接口的安全边界支撑。
"""

import datetime
import uuid
from functools import wraps

import jwt
from flask import current_app, g, jsonify, request

from utils.database import query_one


def generate_access_token(user_id, role="user", account_type="public"):
    """签发 JWT 访问令牌。

    采用对称签名生成可验证会话载体，用于跨服务调用与前后端分离场景的
    认证传递。

    Args:
        user_id (int | str): 用户唯一标识。
        role (str): 角色声明，用于 RBAC 控制。

    Returns:
        str: 编码后的 JWT 字符串。
    """
    expire_minutes = current_app.config.get("JWT_ACCESS_MINUTES", 30)
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "exp": now + datetime.timedelta(minutes=expire_minutes),
        "iat": now,
        "nbf": now,
        "sub": str(user_id),
        "role": role,
        "account_type": account_type,
        "token_type": "access",
        "jti": uuid.uuid4().hex,
        "iss": current_app.config["JWT_ISSUER"],
        "aud": current_app.config["JWT_AUDIENCE"],
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def _extract_bearer_token():
    """从请求头解析 Bearer 令牌。

    Args:
        None.

    Returns:
        str | None: 令牌字符串，若不存在或格式非法则返回 None。
    """
    auth_header = request.headers.get("Authorization", "").strip()
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]

    return None


def login_required(f):
    """认证拦截装饰器。

    在请求进入业务处理前完成令牌校验，并注入用户上下文信息，作为旅游
    信息系统统一鉴权链路的一部分。

    Args:
        f (Callable): 被装饰的路由处理函数。

    Returns:
        Callable: 包装后的可调用对象。
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        """执行令牌校验并注入用户上下文。

        Args:
            *args (tuple): 透传的位置参数。
            **kwargs (dict): 透传的关键字参数。

        Returns:
            Response: 认证失败返回错误响应，成功则继续执行业务逻辑。
        """
        token = _extract_bearer_token()
        if not token:
            return jsonify({"code": 401, "error": "认证失败：缺少或非法的 Authorization Bearer Token"}), 401

        try:
            payload = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"],
                issuer=current_app.config["JWT_ISSUER"],
                audience=current_app.config["JWT_AUDIENCE"],
                options={
                    "require": [
                        "exp",
                        "iat",
                        "nbf",
                        "sub",
                        "jti",
                        "iss",
                        "aud",
                        "token_type",
                        "account_type",
                    ]
                },
            )
            if payload.get("token_type") != "access":
                raise jwt.InvalidTokenError("unexpected token type")
            # g 的生命周期仅限当前请求，适合承载认证上下文且不会污染请求对象。
            # JWT 的 sub 按规范存为字符串；进入应用上下文后统一还原为数据库主键类型。
            g.current_user_id = int(payload["sub"])
            g.current_user_role = payload.get("role", "user")
            g.current_account_type = payload["account_type"]
        except jwt.ExpiredSignatureError:
            return jsonify({"code": 401, "error": "认证失败：令牌已过期"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"code": 401, "error": "认证失败：令牌无效"}), 401

        try:
            if g.current_account_type == "admin":
                active_user = query_one(
                    "SELECT id FROM sys_user WHERE id = %s AND role = 'admin'",
                    (g.current_user_id,),
                )
            elif g.current_account_type == "public":
                active_user = query_one(
                    "SELECT id FROM sys_public_user WHERE id = %s",
                    (g.current_user_id,),
                )
            else:
                return jsonify({"code": 401, "error": "认证失败：账号类型无效"}), 401
        except Exception:
            current_app.logger.exception("Failed to verify active account")
            return jsonify({"code": 503, "error": "认证服务暂不可用"}), 503
        if not active_user:
            return jsonify({"code": 401, "error": "账号已失效，请重新登录"}), 401

        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    """管理员权限拦截装饰器。

    在已认证的基础上进行角色约束，用于保护后台管理与内容治理接口。

    Args:
        f (Callable): 被装饰的路由处理函数。

    Returns:
        Callable: 包装后的可调用对象。
    """

    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        """校验管理员角色。

        Args:
            *args (tuple): 透传的位置参数。
            **kwargs (dict): 透传的关键字参数。

        Returns:
            Response: 角色不足时返回 403，否则继续执行业务逻辑。
        """
        current_role = getattr(g, "current_user_role", None)
        if current_role != "admin" or getattr(g, "current_account_type", None) != "admin":
            return jsonify({"code": 403, "error": "访问拒绝：需要管理员权限"}), 403
        return f(*args, **kwargs)

    return decorated
