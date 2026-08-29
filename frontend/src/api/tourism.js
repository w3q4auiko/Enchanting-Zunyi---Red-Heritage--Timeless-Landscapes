/**
 * 旅游业务 API 访问封装模块。
 *
 * 该模块提供统一的数据访问入口，屏蔽后端接口细节，
 * 作为前端领域层与服务层之间的适配边界。
 */

import request from "@/utils/request";

/**
 * 获取首页轮播图数据。
 * @returns {Promise<any>} 轮播图数据列表。
 */
export function getBanners() {
  return request({
    url: "/banners",
    method: "get",
  });
}

/**
 * 获取行政区划信息。
 * @returns {Promise<any>} 区域数据列表。
 */
export function getRegions() {
  return request({
    url: "/regions",
    method: "get",
  });
}

/**
 * 获取景区列表。
 * @param {string} category - 景区类别筛选条件。
 * @returns {Promise<any>} 景区数据列表。
 */
export function getAttractions(category) {
  return request({
    url: "/attractions",
    method: "get",
    params: { category },
  });
}

/**
 * 获取美食列表。
 * @param {string} category - 美食类别筛选条件。
 * @returns {Promise<any>} 美食数据列表。
 */
export function getFoods(category) {
  return request({
    url: "/foods",
    method: "get",
    params: { category },
  });
}

/**
 * 获取美食街区列表。
 * @returns {Promise<any>} 美食街区数据列表。
 */
export function getFoodStreets() {
  return request({
    url: "/food-streets",
    method: "get",
  });
}

/**
 * 获取旅游路线列表。
 * @param {string} category - 路线类别筛选条件。
 * @returns {Promise<any>} 路线数据列表。
 */
export function getRoutes(category) {
  return request({
    url: "/routes",
    method: "get",
    params: { category },
  });
}

/**
 * 获取资源详情。
 * @param {string | number} id - 资源主键。
 * @param {string} type - 资源类型。
 * @returns {Promise<any>} 详情数据。
 */
export function getDetail(id, type) {
  const typeAliasMap = {
    scenery: "attraction",
    "food-street": "food_street",
  };

  const normalizedType = typeAliasMap[type] || type;

  return request({
    url: `/attraction/${id}`,
    method: "get",
    params: { type: normalizedType },
  });
}
