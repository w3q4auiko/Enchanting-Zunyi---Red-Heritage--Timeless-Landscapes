"""全局配置与环境解析模块。

本模块集中解析环境变量并构建配置容器，遵循配置外置与环境分层原则。
通过生产环境强校验与安全基线约束，保证旅游信息系统在多环境部署时的
一致性与风险可控。
"""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

base_env = PROJECT_ROOT / ".env"
load_dotenv(base_env, override=False)

_raw_env = os.environ.get("APP_ENV", "local").strip().lower()
env_file = ".env.production" if _raw_env in {"prod", "production"} else ".env.local"
env_path = PROJECT_ROOT / env_file
if env_path.exists():
    load_dotenv(env_path, override=True)


class Config:
    """核心配置容器。

    统一承载应用运行参数、认证安全策略、跨域白名单与数据库连接设置，
    其中数据库配置支撑景区、美食、路线等核心业务数据服务的稳定访问。

    Attributes:
        APP_ENV (str): 运行环境标识。
        IS_PRODUCTION (bool): 是否生产环境。
        DEBUG (bool): 调试开关。
        JSON_AS_ASCII (bool): JSON 输出编码策略。
        SECRET_KEY (str): 令牌签名密钥。
        JWT_ACCESS_MINUTES (int): 访问令牌有效期（分钟）。
        MAX_CONTENT_LENGTH (int): 请求体大小上限（字节）。
        CORS_ORIGINS (list[str]): 跨域白名单。
        DB_CONFIG (dict[str, object]): 数据库连接与连接池参数。
    """

    APP_ENV = os.environ.get("APP_ENV", "local").strip().lower()
    IS_PRODUCTION = APP_ENV in {"prod", "production"}

    _raw_debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    if IS_PRODUCTION and _raw_debug:
        raise RuntimeError("生产环境禁止开启 FLASK_DEBUG，请将其设置为 False")
    DEBUG = _raw_debug if not IS_PRODUCTION else False
    JSON_AS_ASCII = False

    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        if IS_PRODUCTION:
            raise RuntimeError("生产环境异常：缺失强制要求的 SECRET_KEY 环境变量")
        SECRET_KEY = "local-dev-secret-key"
    if IS_PRODUCTION and (len(SECRET_KEY) < 32 or SECRET_KEY.startswith("replace-with-")):
        raise RuntimeError("生产环境 SECRET_KEY 必须是至少 32 位的随机字符串")

    JWT_ACCESS_MINUTES = int(os.environ.get("JWT_ACCESS_MINUTES", 30))
    JWT_ISSUER = os.environ.get("JWT_ISSUER", "zunyi-tourism-api").strip()
    JWT_AUDIENCE = os.environ.get("JWT_AUDIENCE", "zunyi-tourism-web").strip()
    AUTH_REFRESH_DAYS = int(os.environ.get("AUTH_REFRESH_DAYS", 30))
    AUTH_LOGIN_MAX_FAILURES = int(os.environ.get("AUTH_LOGIN_MAX_FAILURES", 5))
    AUTH_LOGIN_WINDOW_MINUTES = int(os.environ.get("AUTH_LOGIN_WINDOW_MINUTES", 15))
    AUTH_REGISTER_MAX_PER_HOUR = int(os.environ.get("AUTH_REGISTER_MAX_PER_HOUR", 5))
    AUTH_COOKIE_NAME = os.environ.get("AUTH_COOKIE_NAME", "zunyi_refresh_token").strip()
    AUTH_COOKIE_SECURE = IS_PRODUCTION
    AUTH_COOKIE_SAMESITE = os.environ.get("AUTH_COOKIE_SAMESITE", "Lax").strip()
    TRUST_PROXY = os.environ.get("TRUST_PROXY", "false").lower() == "true"
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 8 * 1024 * 1024))
    MAX_IMAGE_UPLOAD_BYTES = int(
        os.environ.get("MAX_IMAGE_UPLOAD_BYTES", 5 * 1024 * 1024)
    )
    _upload_root_value = Path(os.environ.get("UPLOAD_ROOT", "backend/uploads"))
    UPLOAD_ROOT = (
        _upload_root_value
        if _upload_root_value.is_absolute()
        else PROJECT_ROOT / _upload_root_value
    ).resolve()

    if not 5 <= JWT_ACCESS_MINUTES <= 60:
        raise RuntimeError("JWT_ACCESS_MINUTES 必须在 5–60 分钟之间")
    if not 1 <= AUTH_REFRESH_DAYS <= 90:
        raise RuntimeError("AUTH_REFRESH_DAYS 必须在 1–90 天之间")
    if not 1 <= AUTH_LOGIN_MAX_FAILURES <= 20:
        raise RuntimeError("AUTH_LOGIN_MAX_FAILURES 必须在 1–20 之间")
    if not 1 <= AUTH_LOGIN_WINDOW_MINUTES <= 1440:
        raise RuntimeError("AUTH_LOGIN_WINDOW_MINUTES 必须在 1–1440 分钟之间")
    if not 1 <= AUTH_REGISTER_MAX_PER_HOUR <= 100:
        raise RuntimeError("AUTH_REGISTER_MAX_PER_HOUR 必须在 1–100 之间")
    if not JWT_ISSUER or not JWT_AUDIENCE or not AUTH_COOKIE_NAME:
        raise RuntimeError("JWT 签发方、受众和认证 Cookie 名称不能为空")
    if AUTH_COOKIE_SAMESITE not in {"Lax", "Strict", "None"}:
        raise RuntimeError("AUTH_COOKIE_SAMESITE 只能是 Lax、Strict 或 None")
    if AUTH_COOKIE_SAMESITE == "None" and not AUTH_COOKIE_SECURE:
        raise RuntimeError("SameSite=None 必须配合 Secure Cookie 使用")

    _raw_cors = os.environ.get("CORS_ORIGINS", "").strip()
    if _raw_cors:
        CORS_ORIGINS = [origin.strip() for origin in _raw_cors.split(",") if origin.strip()]
    elif IS_PRODUCTION:
        raise RuntimeError("生产环境异常：缺失强制要求的 CORS_ORIGINS 跨域白名单策略")
    else:
        CORS_ORIGINS = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:80",
            "http://127.0.0.1:80",
        ]

    SITE_URL = os.environ.get("SITE_URL", "").strip().rstrip("/")

    DB_CONFIG = {
        "host": os.environ.get("DB_HOST", "127.0.0.1"),
        "port": int(os.environ.get("DB_PORT", 3306)),
        "user": os.environ.get("DB_USER", "root"),
        "password": os.environ.get("DB_PASSWORD", ""),
        "database": os.environ.get("DB_NAME", "zunyi_tourism"),
        "pool_size": int(os.environ.get("DB_POOL_SIZE", 20)),
        "pool_name": os.environ.get("DB_POOL_NAME", "zunyi_pool"),
        "autocommit": os.environ.get("DB_AUTOCOMMIT", "true").lower() == "true",
        "connect_timeout": int(os.environ.get("DB_CONNECT_TIMEOUT", 5)),
        "read_timeout": int(os.environ.get("DB_READ_TIMEOUT", 10)),
        "write_timeout": int(os.environ.get("DB_WRITE_TIMEOUT", 10)),
    }

    if IS_PRODUCTION:
        if "*" in CORS_ORIGINS:
            raise RuntimeError("生产环境使用凭证 Cookie 时禁止 CORS 通配符来源")
        required_db_envs = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
        missing = [key for key in required_db_envs if not os.environ.get(key)]
        if missing:
            raise RuntimeError(
                f"生产环境异常：缺失强制要求的数据库环境变量配置 -> {', '.join(missing)}"
            )
