"""后台管理接口模块。

该模块基于蓝图提供后台管理端的 CRUD 与统计接口，结合认证与 RBAC
控制，实现对景区、美食、路线、区域与用户数据的集中治理。
"""

from flask import Blueprint, current_app, g, jsonify, request

from utils.auth_helper import admin_required
from utils.database import DBManager, query_all, query_one
from utils.request_data import get_json_body, get_pagination

bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def _run_list_query(base_sql, params, order_sql, page, limit, offset, extra=None):
    """执行通用列表查询并返回结构化响应。

    Args:
        base_sql (str): 基础查询 SQL。
        params (list | tuple): SQL 参数。
        order_sql (str): 排序片段。
        page (int): 页码。
        limit (int): 分页大小。
        offset (int): 偏移量。
        extra (dict | None): 附加到响应中的元数据。

    Returns:
        Response: 含总数与列表数据的 JSON 响应。
    """
    count_sql = f"SELECT COUNT(*) as total FROM ({base_sql}) t"
    total_row = query_one(count_sql, params)
    total = (total_row or {}).get("total", 0)

    data_sql = f"{base_sql} {order_sql} LIMIT %s OFFSET %s"
    data = query_all(data_sql, [*params, limit, offset])
    payload = {"code": 200, "data": data, "total": total}
    if extra:
        payload.update(extra)
    return jsonify(payload)


@bp.route("/attractions", methods=["GET"])
@admin_required
def list_attractions():
    """景区资源列表接口。

    为后台管理提供景区资源的分页与条件筛选能力，用于内容治理与数据维护。

    Args:
        None.

    Returns:
        Response: 景区列表数据的 JSON 响应。
    """
    try:
        page, limit, offset = get_pagination()
        keyword = (request.args.get("keyword") or "").strip()
        status = request.args.get("status")

        sql = "SELECT * FROM sys_attraction WHERE 1=1"
        params = []

        if keyword:
            sql += " AND title LIKE %s"
            params.append(f"%{keyword}%")
        if status not in (None, ""):
            sql += " AND status = %s"
            params.append(int(status))

        return _run_list_query(sql, params, "ORDER BY id DESC", page, limit, offset)
    except ValueError:
        return jsonify({"error": "参数错误"}), 400
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/attractions/<int:item_id>", methods=["GET"])
@admin_required
def get_attraction(item_id):
    """景区资源详情接口。

    按主键返回单个景区资源详情，用于后台编辑与审核。

    Args:
        item_id (int): 景区资源主键。

    Returns:
        Response: 景区详情的 JSON 响应。
    """
    try:
        row = query_one("SELECT * FROM sys_attraction WHERE id = %s", (item_id,))
        if not row:
            return jsonify({"error": "未找到该景点"}), 404
        return jsonify({"code": 200, "data": row})
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/attractions", methods=["POST"])
@admin_required
def add_attraction():
    """景区资源创建接口。

    新增景区资源记录，支撑旅游内容库的扩展与管理端编辑流程。

    Args:
        None.

    Returns:
        Response: 创建结果的 JSON 响应。
    """
    data = get_json_body()
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "标题不能为空"}), 400

    sql = """
        INSERT INTO sys_attraction
        (category, title, description, image_url, banner_url, address, ticket_info, opening_hours, slogan, tips,
         latitude, longitude, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        data.get("category", "自然风光"),
        title,
        data.get("description", ""),
        data.get("image_url", ""),
        data.get("banner_url", ""),
        data.get("address", ""),
        data.get("ticket_info", "免费"),
        data.get("opening_hours", "全天"),
        data.get("slogan", ""),
        data.get("tips", ""),
        data.get("latitude", 0),
        data.get("longitude", 0),
        int(data.get("status", 1)),
    )

    try:
        with DBManager() as cursor:
            cursor.execute(sql, params)
        return jsonify({"code": 200, "msg": "创建成功"})
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/attractions/<int:item_id>", methods=["PUT"])
@admin_required
def update_attraction(item_id):
    """景区资源更新接口。

    按主键更新景区资源字段，用于后台内容治理与运营调整。

    Args:
        item_id (int): 景区资源主键。

    Returns:
        Response: 更新结果的 JSON 响应。
    """
    data = get_json_body()
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "标题不能为空"}), 400

    sql = """
        UPDATE sys_attraction
        SET category=%s, title=%s, description=%s, image_url=%s, banner_url=%s,
            address=%s, ticket_info=%s, opening_hours=%s, slogan=%s, tips=%s,
            latitude=%s, longitude=%s, status=%s
        WHERE id=%s
    """
    params = (
        data.get("category", "自然风光"),
        title,
        data.get("description", ""),
        data.get("image_url", ""),
        data.get("banner_url", ""),
        data.get("address", ""),
        data.get("ticket_info", "免费"),
        data.get("opening_hours", "全天"),
        data.get("slogan", ""),
        data.get("tips", ""),
        data.get("latitude", 0),
        data.get("longitude", 0),
        int(data.get("status", 1)),
        item_id,
    )

    try:
        with DBManager() as cursor:
            affected = cursor.execute(sql, params)
        if affected == 0:
            return jsonify({"error": "未找到该景点"}), 404
        return jsonify({"code": 200, "msg": "更新成功"})
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/attractions/<int:item_id>", methods=["DELETE"])
@admin_required
def delete_attraction(item_id):
    """景区资源删除接口。

    按主键删除景区资源，用于后台内容治理与无效数据清理。

    Args:
        item_id (int): 景区资源主键。

    Returns:
        Response: 删除结果的 JSON 响应。
    """
    try:
        with DBManager() as cursor:
            affected = cursor.execute("DELETE FROM sys_attraction WHERE id = %s", (item_id,))
        if affected == 0:
            return jsonify({"error": "未找到该景点"}), 404
        return jsonify({"code": 200, "msg": "删除成功"})
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/foods", methods=["GET"])
@admin_required
def list_foods():
    """美食资源列表接口。

    为后台管理提供美食资源的分页与筛选能力，用于内容维护与展示控制。

    Args:
        None.

    Returns:
        Response: 美食列表数据的 JSON 响应。
    """
    try:
        page, limit, offset = get_pagination()
        keyword = (request.args.get("keyword") or "").strip()
        status = request.args.get("status")

        sql = "SELECT * FROM sys_food WHERE 1=1"
        params = []
        if keyword:
            sql += " AND name LIKE %s"
            params.append(f"%{keyword}%")
        if status not in (None, ""):
            sql += " AND status = %s"
            params.append(int(status))

        return _run_list_query(sql, params, "ORDER BY id DESC", page, limit, offset)
    except ValueError:
        return jsonify({"error": "参数错误"}), 400
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/foods/<int:item_id>", methods=["GET"])
@admin_required
def get_food(item_id):
    """美食资源详情接口。

    按主键返回美食详情，用于后台编辑与审核。

    Args:
        item_id (int): 美食资源主键。

    Returns:
        Response: 美食详情的 JSON 响应。
    """
    try:
        row = query_one("SELECT * FROM sys_food WHERE id = %s", (item_id,))
        if not row:
            return jsonify({"error": "未找到该美食"}), 404
        return jsonify({"code": 200, "data": row})
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/foods", methods=["POST"])
@admin_required
def add_food():
    """美食资源创建接口。

    新增美食资源记录，丰富旅游系统的餐饮内容库。

    Args:
        None.

    Returns:
        Response: 创建结果的 JSON 响应。
    """
    data = get_json_body()
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "名称不能为空"}), 400

    sql = """
        INSERT INTO sys_food
        (category, name, slogan, recommend_shop, description, image_url, banner_url, address, price, tips, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        data.get("category", "遵义粉面"),
        name,
        data.get("slogan", ""),
        data.get("recommend_shop", ""),
        data.get("description", ""),
        data.get("image_url", ""),
        data.get("banner_url", ""),
        data.get("address", ""),
        data.get("price", ""),
        data.get("tips", ""),
        int(data.get("status", 1)),
    )

    try:
        with DBManager() as cursor:
            cursor.execute(sql, params)
        return jsonify({"code": 200, "msg": "创建成功"})
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/foods/<int:item_id>", methods=["PUT"])
@admin_required
def update_food(item_id):
    """美食资源更新接口。

    按主键更新美食资源字段，用于后台内容治理与运营调整。

    Args:
        item_id (int): 美食资源主键。

    Returns:
        Response: 更新结果的 JSON 响应。
    """
    data = get_json_body()
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "名称不能为空"}), 400

    sql = """
        UPDATE sys_food
        SET category=%s, name=%s, slogan=%s, recommend_shop=%s, description=%s,
            image_url=%s, banner_url=%s, address=%s, price=%s, tips=%s, status=%s
        WHERE id=%s
    """
    params = (
        data.get("category", "遵义粉面"),
        name,
        data.get("slogan", ""),
        data.get("recommend_shop", ""),
        data.get("description", ""),
        data.get("image_url", ""),
        data.get("banner_url", ""),
        data.get("address", ""),
        data.get("price", ""),
        data.get("tips", ""),
        int(data.get("status", 1)),
        item_id,
    )

    try:
        with DBManager() as cursor:
            affected = cursor.execute(sql, params)
        if affected == 0:
            return jsonify({"error": "未找到该美食"}), 404
        return jsonify({"code": 200, "msg": "更新成功"})
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/foods/<int:item_id>", methods=["DELETE"])
@admin_required
def delete_food(item_id):
    """美食资源删除接口。

    按主键删除美食资源，用于后台内容治理与无效数据清理。

    Args:
        item_id (int): 美食资源主键。

    Returns:
        Response: 删除结果的 JSON 响应。
    """
    try:
        with DBManager() as cursor:
            affected = cursor.execute("DELETE FROM sys_food WHERE id = %s", (item_id,))
        if affected == 0:
            return jsonify({"error": "未找到该美食"}), 404
        return jsonify({"code": 200, "msg": "删除成功"})
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/food-streets", methods=["GET"])
@admin_required
def list_food_streets():
    """美食街区列表接口。

    为后台管理提供街区资源的分页查询能力，支撑街区内容维护。

    Args:
        None.

    Returns:
        Response: 街区列表数据的 JSON 响应。
    """
    try:
        page, limit, offset = get_pagination()
        keyword = (request.args.get("keyword") or "").strip()

        sql = "SELECT * FROM sys_food_street WHERE 1=1"
        params = []
        if keyword:
            sql += " AND name LIKE %s"
            params.append(f"%{keyword}%")

        return _run_list_query(sql, params, "ORDER BY id DESC", page, limit, offset)
    except ValueError:
        return jsonify({"error": "参数错误"}), 400
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/food-streets/<int:item_id>", methods=["GET"])
@admin_required
def get_food_street(item_id):
    """美食街区详情接口。

    按主键返回街区详情，用于后台编辑与审核。

    Args:
        item_id (int): 街区资源主键。

    Returns:
        Response: 街区详情的 JSON 响应。
    """
    try:
        row = query_one("SELECT * FROM sys_food_street WHERE id = %s", (item_id,))
        if not row:
            return jsonify({"error": "未找到该街区"}), 404
        return jsonify({"code": 200, "data": row})
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/food-streets", methods=["POST"])
@admin_required
def add_food_street():
    """美食街区创建接口。

    新增美食街区记录，完善旅游系统餐饮街区数据。

    Args:
        None.

    Returns:
        Response: 创建结果的 JSON 响应。
    """
    data = get_json_body()
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "名称不能为空"}), 400

    sql = """
        INSERT INTO sys_food_street
        (name, alias, address, description, recommend_tags, image_url, banner_url, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        name,
        data.get("alias", ""),
        data.get("address", ""),
        data.get("description", ""),
        data.get("recommend_tags", ""),
        data.get("image_url", ""),
        data.get("banner_url", ""),
        int(data.get("status", 1)),
    )

    try:
        with DBManager() as cursor:
            cursor.execute(sql, params)
        return jsonify({"code": 200, "msg": "创建成功"})
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/food-streets/<int:item_id>", methods=["PUT"])
@admin_required
def update_food_street(item_id):
    """美食街区更新接口。

    按主键更新街区字段，用于后台内容治理与运营调整。

    Args:
        item_id (int): 街区资源主键。

    Returns:
        Response: 更新结果的 JSON 响应。
    """
    data = get_json_body()
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "名称不能为空"}), 400

    sql = """
        UPDATE sys_food_street
        SET name=%s, alias=%s, address=%s, description=%s,
            recommend_tags=%s, image_url=%s, banner_url=%s, status=%s
        WHERE id=%s
    """
    params = (
        name,
        data.get("alias", ""),
        data.get("address", ""),
        data.get("description", ""),
        data.get("recommend_tags", ""),
        data.get("image_url", ""),
        data.get("banner_url", ""),
        int(data.get("status", 1)),
        item_id,
    )

    try:
        with DBManager() as cursor:
            affected = cursor.execute(sql, params)
        if affected == 0:
            return jsonify({"error": "未找到该街区"}), 404
        return jsonify({"code": 200, "msg": "更新成功"})
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/food-streets/<int:item_id>", methods=["DELETE"])
@admin_required
def delete_food_street(item_id):
    """美食街区删除接口。

    按主键删除街区资源，用于后台内容治理与无效数据清理。

    Args:
        item_id (int): 街区资源主键。

    Returns:
        Response: 删除结果的 JSON 响应。
    """
    try:
        with DBManager() as cursor:
            affected = cursor.execute("DELETE FROM sys_food_street WHERE id = %s", (item_id,))
        if affected == 0:
            return jsonify({"error": "未找到该街区"}), 404
        return jsonify({"code": 200, "msg": "删除成功"})
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/regions", methods=["GET"])
@admin_required
def list_regions():
    """区域列表接口。

    返回区域资源的分页与筛选结果，用于前台导航与内容维护的管理入口。

    Args:
        None.

    Returns:
        Response: 区域列表数据的 JSON 响应。
    """
    try:
        page, limit, offset = get_pagination(default_limit=14)
        keyword = (request.args.get("keyword") or "").strip()

        sql = "SELECT * FROM sys_region WHERE 1=1"
        params = []
        if keyword:
            sql += " AND (name LIKE %s OR alias LIKE %s)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])

        return _run_list_query(sql, params, "ORDER BY sort_order ASC, id ASC", page, limit, offset)
    except ValueError:
        return jsonify({"error": "参数错误"}), 400
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/regions/<int:region_id>", methods=["GET"])
@admin_required
def get_region(region_id):
    """区域详情接口。

    按主键返回区域详情，用于后台编辑与审核。

    Args:
        region_id (int): 区域资源主键。

    Returns:
        Response: 区域详情的 JSON 响应。
    """
    try:
        row = query_one("SELECT * FROM sys_region WHERE id = %s", (region_id,))
        if not row:
            return jsonify({"error": "未找到该区域"}), 404
        return jsonify({"code": 200, "data": row})
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/regions", methods=["POST"])
@admin_required
def add_region():
    """区域创建接口。

    新增区域资源记录，完善旅游目的地的组织结构与导航维度。

    Args:
        None.

    Returns:
        Response: 创建结果的 JSON 响应。
    """
    data = get_json_body()
    name = (data.get("name") or "").strip()
    region_type = (data.get("type") or "").strip()
    if not name or not region_type:
        return jsonify({"error": "名称和类型不能为空"}), 400

    sql = """
        INSERT INTO sys_region
        (name, type, alias, address, description, banner_url, sort_order, status, longitude, latitude)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        name,
        region_type,
        data.get("alias", ""),
        data.get("address", ""),
        data.get("description", ""),
        data.get("banner_url", ""),
        int(data.get("sort_order", 0)),
        int(data.get("status", 1)),
        data.get("longitude"),
        data.get("latitude"),
    )

    try:
        with DBManager() as cursor:
            cursor.execute(sql, params)
        return jsonify({"code": 200, "msg": "创建成功"})
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/regions/<int:region_id>", methods=["PUT"])
@admin_required
def update_region(region_id):
    """区域更新接口。

    按主键更新区域字段，用于后台内容治理与运营调整。

    Args:
        region_id (int): 区域资源主键。

    Returns:
        Response: 更新结果的 JSON 响应。
    """
    data = get_json_body()
    name = (data.get("name") or "").strip()
    region_type = (data.get("type") or "").strip()
    if not name or not region_type:
        return jsonify({"error": "名称和类型不能为空"}), 400

    sql = """
        UPDATE sys_region
        SET name=%s, type=%s, alias=%s, address=%s, description=%s,
            banner_url=%s, sort_order=%s, status=%s, longitude=%s, latitude=%s
        WHERE id=%s
    """
    params = (
        name,
        region_type,
        data.get("alias", ""),
        data.get("address", ""),
        data.get("description", ""),
        data.get("banner_url", ""),
        int(data.get("sort_order", 0)),
        int(data.get("status", 1)),
        data.get("longitude"),
        data.get("latitude"),
        region_id,
    )

    try:
        with DBManager() as cursor:
            affected = cursor.execute(sql, params)
        if affected == 0:
            return jsonify({"error": "未找到该区域"}), 404
        return jsonify({"code": 200, "msg": "更新成功"})
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/regions/<int:region_id>", methods=["DELETE"])
@admin_required
def delete_region(region_id):
    """区域删除接口。

    按主键删除区域资源，用于后台内容治理与无效数据清理。

    Args:
        region_id (int): 区域资源主键。

    Returns:
        Response: 删除结果的 JSON 响应。
    """
    try:
        with DBManager() as cursor:
            affected = cursor.execute("DELETE FROM sys_region WHERE id = %s", (region_id,))
        if affected == 0:
            return jsonify({"error": "未找到该区域"}), 404
        return jsonify({"code": 200, "msg": "删除成功"})
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/routes", methods=["GET"])
@admin_required
def list_routes():
    """路线列表接口。

    为后台管理提供路线资源的分页与筛选能力，用于线路内容维护。

    Args:
        None.

    Returns:
        Response: 路线列表数据的 JSON 响应。
    """
    try:
        page, limit, offset = get_pagination()
        keyword = (request.args.get("keyword") or "").strip()
        status = request.args.get("status")

        sql = "SELECT * FROM sys_route WHERE 1=1"
        params = []
        if keyword:
            sql += " AND title LIKE %s"
            params.append(f"%{keyword}%")
        if status not in (None, ""):
            sql += " AND status = %s"
            params.append(int(status))

        return _run_list_query(sql, params, "ORDER BY id DESC", page, limit, offset)
    except ValueError:
        return jsonify({"error": "参数错误"}), 400
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/routes/<int:item_id>", methods=["GET"])
@admin_required
def get_route(item_id):
    """路线详情接口。

    按主键返回路线详情，用于后台编辑与审核。

    Args:
        item_id (int): 路线资源主键。

    Returns:
        Response: 路线详情的 JSON 响应。
    """
    try:
        row = query_one("SELECT * FROM sys_route WHERE id = %s", (item_id,))
        if not row:
            return jsonify({"error": "未找到该路线"}), 404
        return jsonify({"code": 200, "data": row})
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/routes", methods=["POST"])
@admin_required
def add_route():
    """路线创建接口。

    新增旅游路线记录，丰富旅游系统的线路内容库。

    Args:
        None.

    Returns:
        Response: 创建结果的 JSON 响应。
    """
    data = get_json_body()
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "标题不能为空"}), 400

    sql = """
        INSERT INTO sys_route
        (category, title, difficulty, distance_km, duration_hours, climb_meters,
         route_type, start_point, address, description, tips, image_url, banner_url,
         latitude, longitude, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        data.get("category", "山野徒步"),
        title,
        data.get("difficulty", 1),
        data.get("distance_km", 0),
        data.get("duration_hours", 0),
        data.get("climb_meters", 0),
        data.get("route_type", "环线"),
        data.get("start_point", ""),
        data.get("address", ""),
        data.get("description", ""),
        data.get("tips", ""),
        data.get("image_url", ""),
        data.get("banner_url", ""),
        data.get("latitude", 0),
        data.get("longitude", 0),
        int(data.get("status", 1)),
    )

    try:
        with DBManager() as cursor:
            cursor.execute(sql, params)
        return jsonify({"code": 200, "msg": "创建成功"})
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/routes/<int:item_id>", methods=["PUT"])
@admin_required
def update_route(item_id):
    """路线更新接口。

    按主键更新路线字段，用于后台内容治理与运营调整。

    Args:
        item_id (int): 路线资源主键。

    Returns:
        Response: 更新结果的 JSON 响应。
    """
    data = get_json_body()
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "标题不能为空"}), 400

    sql = """
        UPDATE sys_route
        SET category=%s, title=%s, difficulty=%s, distance_km=%s, duration_hours=%s,
            climb_meters=%s, route_type=%s, start_point=%s, address=%s, description=%s,
            tips=%s, image_url=%s, banner_url=%s, latitude=%s, longitude=%s, status=%s
        WHERE id=%s
    """
    params = (
        data.get("category", "山野徒步"),
        title,
        data.get("difficulty", 1),
        data.get("distance_km", 0),
        data.get("duration_hours", 0),
        data.get("climb_meters", 0),
        data.get("route_type", "环线"),
        data.get("start_point", ""),
        data.get("address", ""),
        data.get("description", ""),
        data.get("tips", ""),
        data.get("image_url", ""),
        data.get("banner_url", ""),
        data.get("latitude", 0),
        data.get("longitude", 0),
        int(data.get("status", 1)),
        item_id,
    )

    try:
        with DBManager() as cursor:
            affected = cursor.execute(sql, params)
        if affected == 0:
            return jsonify({"error": "未找到该路线"}), 404
        return jsonify({"code": 200, "msg": "更新成功"})
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/routes/<int:item_id>", methods=["DELETE"])
@admin_required
def delete_route(item_id):
    """路线删除接口。

    按主键删除路线资源，用于后台内容治理与无效数据清理。

    Args:
        item_id (int): 路线资源主键。

    Returns:
        Response: 删除结果的 JSON 响应。
    """
    try:
        with DBManager() as cursor:
            affected = cursor.execute("DELETE FROM sys_route WHERE id = %s", (item_id,))
        if affected == 0:
            return jsonify({"error": "未找到该路线"}), 404
        return jsonify({"code": 200, "msg": "删除成功"})
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    """用户列表接口。

    返回后台用户基础信息并支持分页与筛选，用于账号管理与权限审计。

    Args:
        None.

    Returns:
        Response: 用户列表数据的 JSON 响应。
    """
    try:
        page, limit, offset = get_pagination()
        keyword = (request.args.get("keyword") or "").strip()
        account_type = (request.args.get("account_type") or "all").strip()
        if account_type not in {"all", "admin", "public"}:
            raise ValueError

        sql = """
            SELECT id, username, nickname, role, account_type, create_time
            FROM (
                SELECT id, username, nickname, role, 'admin' AS account_type, create_time
                FROM sys_user
                UNION ALL
                SELECT id, username, nickname, 'visitor' AS role,
                       'public' AS account_type, create_time
                FROM sys_public_user
            ) account
            WHERE 1=1
        """
        params = []
        if keyword:
            sql += " AND (username LIKE %s OR nickname LIKE %s)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        if account_type != "all":
            sql += " AND account_type = %s"
            params.append(account_type)

        admin_count = (
            query_one("SELECT COUNT(*) c FROM sys_user WHERE role = 'admin'") or {}
        ).get("c", 0)
        return _run_list_query(
            sql,
            params,
            "ORDER BY create_time DESC, account_type ASC, id DESC",
            page,
            limit,
            offset,
            {"admin_count": admin_count},
        )
    except ValueError:
        return jsonify({"error": "参数错误"}), 400
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/users/<account_type>/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(account_type, user_id):
    """用户删除接口。

    注销后台用户账号并保留关键管理员保护规则，确保权限边界稳定。

    Args:
        account_type (str): 账号域，支持 admin 或 public。
        user_id (int): 用户主键。

    Returns:
        Response: 删除结果的 JSON 响应。
    """
    if account_type not in {"admin", "public"}:
        return jsonify({"error": "账号类型不存在"}), 404

    if account_type == "admin" and user_id == g.current_user_id:
        return jsonify({"error": "不能删除当前登录账号"}), 403

    try:
        with DBManager(transactional=True) as cursor:
            if account_type == "admin":
                cursor.execute("SELECT id FROM sys_user WHERE role = 'admin' FOR UPDATE")
                admin_ids = {row["id"] for row in cursor.fetchall()}
                if user_id not in admin_ids:
                    return jsonify({"error": "管理员账号不存在"}), 404
                if len(admin_ids) <= 1:
                    return jsonify({"error": "必须至少保留一个管理员"}), 403
                table_name = "sys_user"
            else:
                cursor.execute(
                    "SELECT id FROM sys_public_user WHERE id = %s FOR UPDATE", (user_id,)
                )
                if not cursor.fetchone():
                    return jsonify({"error": "普通用户账号不存在"}), 404
                table_name = "sys_public_user"

            cursor.execute(
                """
                UPDATE sys_auth_refresh_token
                SET revoked_at = UTC_TIMESTAMP(6)
                WHERE account_type = %s AND user_id = %s AND revoked_at IS NULL
                """,
                (account_type, user_id),
            )
            affected = cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", (user_id,))
        if affected == 0:
            return jsonify({"error": "用户不存在"}), 404
        return jsonify({"code": 200, "msg": "删除成功"})
    except Exception:
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route("/stats", methods=["GET"])
@admin_required
def get_stats():
    """后台统计指标接口。

    聚合系统核心数据量，支撑管理端仪表盘的运营态势展示。

    Args:
        None.

    Returns:
        Response: 统计指标的 JSON 响应。
    """
    try:
        return jsonify(
            {
                "code": 200,
                "admin_count": (query_one("SELECT COUNT(*) c FROM sys_user") or {}).get("c", 0),
                "public_user_count": (
                    query_one("SELECT COUNT(*) c FROM sys_public_user") or {}
                ).get("c", 0),
                "attraction_count": (query_one("SELECT COUNT(*) c FROM sys_attraction") or {}).get("c", 0),
                "food_count": (query_one("SELECT COUNT(*) c FROM sys_food") or {}).get("c", 0),
                "food_street_count": (
                    query_one("SELECT COUNT(*) c FROM sys_food_street") or {}
                ).get("c", 0),
                "region_count": (query_one("SELECT COUNT(*) c FROM sys_region") or {}).get("c", 0),
                "route_count": (query_one("SELECT COUNT(*) c FROM sys_route") or {}).get("c", 0),
            }
        )
    except Exception:
        # 统计页同时依赖多张业务表，记录完整异常便于快速定位缺表或结构不兼容问题。
        current_app.logger.exception("Failed to aggregate dashboard statistics")
        return jsonify({"error": "无法获取统计数据"}), 500
