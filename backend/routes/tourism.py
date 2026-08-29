"""公共旅游业务聚合模块。

该模块向游客提供只读数据接口与聚合检索能力，通过发布状态过滤与
统一字段投影保证对外数据的一致性与可展示性。
"""

from flask import Blueprint, jsonify, request

from utils.database import query_all, query_one

bp = Blueprint("tourism", __name__, url_prefix="/api")


@bp.route("/banners")
def get_banners():
    """轮播图数据聚合接口。

    面向首页展示聚合多实体轮播数据，统一字段映射以降低前端适配成本。

    Args:
        None.

    Returns:
        Response: 轮播数据列表的 JSON 响应。
    """
    sql = """
          SELECT id,
                 IFNULL(banner_title, title)      as title,
                 IFNULL(banner_desc, description) as description,
                 banner_url,
                 image_url,
                 is_banner                        as sort_order,
                 'scenery'                        as entity_type
          FROM sys_attraction
          WHERE is_banner > 0 AND status = 1

          UNION ALL

          SELECT id,
                 IFNULL(banner_title, name) as title,
                 banner_desc,
                 banner_url,
                 image_url,
                 sort_order                 as sort_order,
                 'food'                     as entity_type
          FROM sys_food
          WHERE sort_order > 0 AND status = 1

          ORDER BY sort_order ASC
          """
    try:
        data = query_all(sql)
        return jsonify(data if data else [])
    except Exception:
        return jsonify([])


@bp.route("/regions", methods=["GET"])
def list_regions():
    """行政区划数据检索接口。

    返回已发布区域信息，支撑前台导航与目的地筛选。

    Args:
        None.

    Returns:
        Response: 区域数据列表的 JSON 响应。
    """
    try:
        sql = "SELECT * FROM sys_region WHERE status = 1 ORDER BY sort_order ASC"
        data = query_all(sql)
        return jsonify(data if data else [])
    except Exception:
        return jsonify({"error": "数据检索失败：无法获取行政区划信息"}), 500


@bp.route("/attractions", methods=["GET"])
def get_attractions_list():
    """景区资源列表接口。

    提供按类别筛选的景区查询能力，面向前台景点列表页输出已发布资源。

    Args:
        None.

    Returns:
        Response: 景区数据列表的 JSON 响应。
    """
    category = request.args.get("category")
    sql = "SELECT * FROM sys_attraction WHERE status = 1"
    params = []

    if category:
        sql += " AND category = %s"
        params.append(category)

    sql += " ORDER BY id ASC"

    try:
        data = query_all(sql, params)
        return jsonify(data if data else [])
    except Exception:
        return jsonify({"error": "数据检索失败：无法获取景点列表"}), 500


@bp.route("/list/<string:entity_type>")
def fetch_list_data(entity_type):
    """多类型列表数据接口。

    通过统一入口按实体类型返回轻量化列表数据，为首页与专题页提供
    标准化数据输出。

    Args:
        entity_type (str): 实体类型标识（scenery/food/route）。

    Returns:
        Response: 列表数据的 JSON 响应。
    """
    try:
        limit = int(request.args.get("limit", 6))
    except (TypeError, ValueError):
        return jsonify({"error": "参数错误：limit 必须为整数"}), 400

    limit = max(1, min(limit, 50))

    if entity_type == "scenery":
        sql = "SELECT id, title, description, image_url, 'scenery' as entity_type FROM sys_attraction WHERE status = 1 ORDER BY id DESC LIMIT %s"
    elif entity_type == "food":
        sql = "SELECT id, name as title, description, image_url, 'food' as entity_type FROM sys_food WHERE status = 1 ORDER BY id DESC LIMIT %s"
    elif entity_type == "route":
        sql = "SELECT id, title, description, image_url, 'route' as entity_type FROM sys_route WHERE status = 1 ORDER BY id DESC LIMIT %s"
    else:
        return jsonify([])

    try:
        data = query_all(sql, (limit,))
        return jsonify(data if data else [])
    except Exception:
        return jsonify({"error": f"数据检索失败：无法获取 {entity_type} 列表"}), 500


@bp.route("/attraction/<int:item_id>")
def get_attraction_detail(item_id):
    """统一详情查询接口。

    依据实体类型映射到对应数据表与字段集合，输出标准化详情数据，
    降低前端详情页的适配成本。

    Args:
        item_id (int): 资源主键。

    Returns:
        Response: 详情数据的 JSON 响应。
    """
    entity_type = request.args.get("type", "attraction")

    sql_map = {
        "food": """
            SELECT id, category, name as title, slogan, description, image_url, banner_url, address,
                   '全天供应' as opening_hours, price as ticket_info, tips, recommend_shop,
                   'food' as entity_type
            FROM sys_food WHERE id = %s
        """,
        "route": """
            SELECT id, category, title, difficulty, distance_km, duration_hours,
                   climb_meters, route_type, start_point, address, description,
                   image_url, banner_url, tips, latitude, longitude,
                   '全天开放' as opening_hours, '免费' as ticket_info,
                   'route' as entity_type
            FROM sys_route WHERE id = %s
        """,
        "region": """
            SELECT id, name as title, description, banner_url, address,
                   '全天开放' as opening_hours, '免费' as ticket_info,
                   'region' as entity_type, longitude, latitude
            FROM sys_region WHERE id = %s
        """,
        "food_street": """
            SELECT id, name, alias, description, image_url, banner_url, address,
                   recommend_tags, 'food_street' as entity_type
            FROM sys_food_street WHERE id = %s
        """,
        "attraction": """
            SELECT id, category, title, description, image_caption, image_url, banner_url,
                   address, opening_hours, ticket_info, tips, latitude, longitude,
                   'scenery' as entity_type
            FROM sys_attraction WHERE id = %s
        """,
    }

    sql = sql_map.get(entity_type)
    if not sql:
        return jsonify({"error": "参数错误：不支持的 type"}), 400

    try:
        data = query_one(sql, (item_id,))
        if data:
            return jsonify(data)
        return jsonify({"error": "资源未找到"}), 404
    except Exception:
        return jsonify({"error": "查询详情失败：服务器内部错误"}), 500


@bp.route("/foods", methods=["GET"])
def get_foods_list():
    """美食资源列表接口。

    返回已发布美食数据并支持按类别筛选与排序，面向前台美食专题展示。

    Args:
        None.

    Returns:
        Response: 美食数据列表的 JSON 响应。
    """
    category = request.args.get("category")
    sql = "SELECT * FROM sys_food WHERE status = 1"
    params = []

    if category:
        sql += " AND category = %s"
        params.append(category)

    sql += " ORDER BY sort_order ASC, id DESC"

    try:
        data = query_all(sql, params)
        return jsonify(data if data else [])
    except Exception:
        return jsonify({"error": "数据检索失败：无法获取美食列表"}), 500


@bp.route("/food-streets", methods=["GET"])
def get_food_streets():
    """美食街区列表接口。

    返回已发布美食街区基础信息，用于前台街区推荐与导航。

    Args:
        None.

    Returns:
        Response: 街区数据列表的 JSON 响应。
    """
    try:
        sql = "SELECT id, name, alias, address, description, recommend_tags, image_url, banner_url FROM sys_food_street WHERE status = 1 ORDER BY id DESC"
        data = query_all(sql)
        return jsonify(data if data else [])
    except Exception:
        return jsonify({"error": "数据检索失败：无法获取美食街区信息"}), 500


@bp.route("/routes", methods=["GET"])
def get_routes_list():
    """旅游路线列表接口。

    返回已发布路线数据并支持按类别筛选，满足前台路线推荐与检索需求。

    Args:
        None.

    Returns:
        Response: 路线数据列表的 JSON 响应。
    """
    category = request.args.get("category")
    sql = "SELECT * FROM sys_route WHERE status = 1"
    params = []

    if category:
        sql += " AND category = %s"
        params.append(category)

    sql += " ORDER BY id DESC"

    try:
        data = query_all(sql, params)
        return jsonify(data if data else [])
    except Exception:
        return jsonify({"error": "数据检索失败：无法获取路线列表"}), 500
