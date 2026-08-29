"""HTTP 请求数据解析工具。

集中处理 JSON 请求体与分页参数，避免各蓝图重复实现并保证边界规则一致。
"""

from flask import request


def get_json_body() -> dict:
    """返回字典形式的 JSON 请求体；非对象 JSON 统一视为空对象。"""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def get_pagination(default_limit: int = 10, max_limit: int = 100) -> tuple[int, int, int]:
    """解析并限制分页参数，返回 ``(page, limit, offset)``。"""
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", default_limit))
    except (TypeError, ValueError) as exc:
        raise ValueError("分页参数必须为整数") from exc

    page = max(1, page)
    limit = max(1, min(limit, max_limit))
    return page, limit, (page - 1) * limit
