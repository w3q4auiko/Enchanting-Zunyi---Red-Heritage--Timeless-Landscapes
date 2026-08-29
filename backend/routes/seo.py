"""SEO 基础路由模块。

本模块提供 sitemap.xml 与 robots.txt 资源，作为旅游信息系统对外可发现性的
基础设施，通过聚合静态页面与已发布业务内容提升搜索引擎抓取与索引稳定性。
"""

from xml.sax.saxutils import escape

from flask import Blueprint, Response, current_app, request

from utils.database import query_all

bp = Blueprint("seo", __name__)


def _get_base_url() -> str:
    """获取站点根地址。

    优先使用显式配置的 SITE_URL，避免反向代理与多域部署导致的协议或
    域名误判，确保生成 URL 的一致性与可缓存性。

    Args:
        None.

    Returns:
        str: 站点根地址（不包含末尾斜杠）。
    """
    site_url = current_app.config.get("SITE_URL")
    if site_url:
        return site_url
    return request.host_url.rstrip("/")


def _build_url(base_url: str, path: str) -> str:
    """拼接站点绝对 URL。

    Args:
        base_url (str): 站点根地址。
        path (str): 站点内路径前缀或资源路径。

    Returns:
        str: 组合后的站点绝对 URL。
    """
    return f"{base_url}{path}"


@bp.route("/sitemap.xml")
def sitemap():
    """生成站点 Sitemap XML。

    聚合静态页面与已发布的景区、美食、路线等业务内容，形成可被搜索
    引擎抓取的站点地图，用于提升旅游资源的曝光与检索覆盖。

    Args:
        None.

    Returns:
        Response: application/xml 响应。
    """
    base_url = _get_base_url()

    urls = []
    static_paths = [
        "/",
        "/overview",
        "/highlights",
        "/highlights/list/red",
        "/highlights/list/time",
        "/highlights/list/nature",
        "/taste",
        "/taste/list/noodle",
        "/taste/list/snack",
        "/taste/list/feast",
        "/taste/list/dessert",
        "/taste/list/tea",
        "/taste/list/mountain",
        "/taste/list/gift",
        "/taste/list/streets",
        "/guide",
        "/guide/list/districts",
        "/guide/list/cities",
        "/guide/list/counties",
        "/about",
    ]

    for path in static_paths:
        urls.append(
            {
                "loc": _build_url(base_url, path),
                "changefreq": "weekly",
                "priority": "0.8" if path == "/" else "0.6",
            }
        )

    def append_items(sql: str, path_prefix: str, changefreq: str, priority: str) -> None:
        """追加动态业务资源的站点 URL。

        Args:
            sql (str): 查询资源主键的 SQL 语句。
            path_prefix (str): 资源详情页路径前缀。
            changefreq (str): Sitemap 变更频率字段。
            priority (str): Sitemap 优先级字段。

        Returns:
            None.
        """
        try:
            for row in query_all(sql):
                urls.append(
                    {
                        "loc": _build_url(base_url, f"{path_prefix}{row['id']}"),
                        "changefreq": changefreq,
                        "priority": priority,
                    }
                )
        except Exception:
            current_app.logger.exception("Failed to build sitemap for %s", path_prefix)

    append_items(
        "SELECT id FROM sys_attraction WHERE status = 1",
        "/attraction/scenery/",
        "weekly",
        "0.7",
    )
    append_items(
        "SELECT id FROM sys_food WHERE status = 1",
        "/attraction/food/",
        "weekly",
        "0.6",
    )
    append_items(
        "SELECT id FROM sys_route WHERE status = 1",
        "/attraction/route/",
        "weekly",
        "0.6",
    )
    append_items(
        "SELECT id FROM sys_region WHERE status = 1",
        "/attraction/region/",
        "weekly",
        "0.6",
    )
    append_items(
        "SELECT id FROM sys_food_street WHERE status = 1",
        "/attraction/food-street/",
        "weekly",
        "0.6",
    )

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    for item in urls:
        loc = escape(item["loc"])
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append(f"    <changefreq>{item['changefreq']}</changefreq>")
        lines.append(f"    <priority>{item['priority']}</priority>")
        lines.append("  </url>")

    lines.append("</urlset>")

    response = Response("\n".join(lines), mimetype="application/xml")
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response


@bp.route("/robots.txt")
def robots():
    """生成 robots.txt。

    以最小化规则声明站点可抓取范围，并提供 Sitemap 入口，保障旅游
    内容在搜索引擎中的标准化索引路径。

    Args:
        None.

    Returns:
        Response: text/plain 响应。
    """
    base_url = _get_base_url()
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {base_url}/sitemap.xml",
    ]
    response = Response("\n".join(lines), mimetype="text/plain")
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response
