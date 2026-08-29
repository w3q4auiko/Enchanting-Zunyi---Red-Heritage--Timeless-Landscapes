"""应用入口与装配模块。

本模块以应用工厂模式（Application Factory）集中构建 Flask 应用，统一装配
跨域策略、蓝图路由与全局异常处理边界，用于支撑遵义旅游信息系统的服务启动
与运行期治理。
"""

import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from commands import register_commands


def create_app():
    """构建并装配 Flask 应用实例。

    该函数是系统装配的唯一入口，遵循应用工厂模式以便环境切换与测试隔离，
    并统一注册跨域策略、业务蓝图与全局异常处理器，向外部暴露健康检查端点。

    Args:
        None.

    Returns:
        Flask: 完成装配的应用实例。
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    if app.config.get("TRUST_PROXY"):
        # 仅在受信任反向代理后启用，确保限流日志取得真实客户端地址与协议。
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    logging.basicConfig(level=logging.INFO)

    cors_origins = app.config.get("CORS_ORIGINS", "*")
    CORS(
        app,
        resources={r"/api/*": {"origins": cors_origins}},
        supports_credentials=True,
    )

    register_blueprints(app)
    register_error_handlers(app)
    register_commands(app)

    @app.after_request
    def apply_security_headers(response):
        """阻止认证响应缓存，并补充通用浏览器安全头。"""
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        if request.path.startswith(("/api/auth/", "/api/public/login", "/api/public/register")):
            response.headers["Cache-Control"] = "no-store"
            response.headers["Pragma"] = "no-cache"
        return response

    @app.route("/")
    def health_check():
        """服务健康探活端点。

        为运维监控与负载均衡提供最小化探活信号，确保旅游信息系统
        API 服务可被稳定接入与观测。

        Args:
            None.

        Returns:
            Response: 标准化 JSON 存活响应。
        """
        return jsonify(
            {
                "code": 200,
                "status": "active",
                "message": "Enchanting Zunyi API Service is Running",
            }
        )

    return app


def register_blueprints(app: Flask) -> None:
    """集中注册业务蓝图。

    采用基于蓝图的模块化路由，将管理端、认证、旅游业务与投稿等域划分为
    独立命名空间，降低耦合并提升系统演进的可维护性。

    Args:
        app (Flask): 应用实例，用于挂载各业务蓝图。

    Returns:
        None.
    """
    try:
        from routes.admin import bp as admin_bp
        from routes.auth import bp as auth_bp
        from routes.public_auth import bp as public_auth_bp
        from routes.media import bp as media_bp
        from routes.seo import bp as seo_bp
        from routes.submission import bp as submission_bp
        from routes.tourism import bp as tourism_bp

        app.register_blueprint(admin_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(public_auth_bp)
        app.register_blueprint(media_bp)
        app.register_blueprint(seo_bp)
        app.register_blueprint(tourism_bp)
        app.register_blueprint(submission_bp)
        app.logger.info("Blueprints registered")
    except Exception:
        app.logger.exception("Failed to register blueprints")
        raise


def register_error_handlers(app: Flask) -> None:
    """注册全局异常处理器。

    该函数构建统一错误边界，规范化 HTTP 异常与未捕获异常的输出结构，
    以避免内部错误细节泄露并保持客户端的稳定契约。

    Args:
        app (Flask): 应用实例，用于注册错误处理器。

    Returns:
        None.
    """

    @app.errorhandler(HTTPException)
    def handle_http_exception(exc: HTTPException):
        """处理可识别的 HTTP 异常。

        Args:
            exc (HTTPException): 已规范化的 HTTP 异常对象。

        Returns:
            Response: 标准化 JSON 错误响应。
        """
        return jsonify({"code": exc.code, "error": exc.description}), exc.code

    @app.errorhandler(Exception)
    def handle_unexpected_exception(exc: Exception):
        """处理未捕获异常。

        Args:
            exc (Exception): 未捕获的异常实例。

        Returns:
            Response: 统一的服务器错误响应。
        """
        app.logger.exception("Unhandled exception: %s", exc)
        return jsonify({"code": 500, "error": "服务器内部错误"}), 500


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=app.config.get("DEBUG", False))
