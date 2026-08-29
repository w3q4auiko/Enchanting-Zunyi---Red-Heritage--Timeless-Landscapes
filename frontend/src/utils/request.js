/**
 * 网络请求基础设施模块。
 *
 * 该模块构建统一的 HTTP 客户端实例，封装鉴权头注入、错误边界
 * 与会话失效处理，形成前端到后端的稳定通信契约。
 */

import axios from "axios";
import { ElMessage } from "element-plus";
import { refreshSession } from "@/api/auth";
import { clearSession, getToken } from "@/utils/session";

const service = axios.create({
  baseURL: "/api",
  timeout: 10000,
  withCredentials: true,
});

/**
 * 请求拦截器：注入鉴权令牌。
 * @param {import("axios").InternalAxiosRequestConfig} config - 请求配置。
 * @returns {import("axios").InternalAxiosRequestConfig} 更新后的配置。
 */
const attachAuthToken = (config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
};

/**
 * 请求拦截器：透传请求异常。
 * @param {unknown} error - 请求错误。
 * @returns {Promise<never>} 拒绝的 Promise。
 */
const handleRequestError = (error) => Promise.reject(error);

service.interceptors.request.use(attachAuthToken, handleRequestError);

/**
 * 响应拦截器：返回业务响应体。
 * @param {import("axios").AxiosResponse} response - 响应对象。
 * @returns {any} 业务数据载荷。
 */
const unwrapResponse = (response) => response.data;

/**
 * 响应拦截器：统一错误处理与会话失效治理。
 * @param {any} error - 响应错误。
 * @returns {Promise<never>} 拒绝的 Promise。
 */
const handleResponseError = async (error) => {
  // 即使业务请求关闭了全局弹窗，401 仍必须先尝试恢复会话。
  if (error.response?.status === 401) {
    if (!error.config?._authRetry) {
      error.config._authRetry = true;
      const refreshed = await refreshSession(true);
      if (refreshed) {
        error.config.headers.Authorization = `Bearer ${getToken()}`;
        return service(error.config);
      }
    }

    clearSession();
    const currentPath = window.location.pathname;
    const publicEntryPaths = ["/login", "/", "/home"];
    const isPublicEntry = publicEntryPaths.includes(currentPath);

    if (!isPublicEntry) {
      ElMessage.warning("登录状态已失效，请重新登录");
      window.location.assign("/login");
    } else if (currentPath === "/") {
      window.location.reload();
    }

    return Promise.reject(error);
  }

  if (error.config?.skipGlobalHandler) {
    return Promise.reject(error);
  }

  if (!axios.isCancel(error)) {
    const message =
      error.response?.data?.error || error.message || "网络请求异常，请稍后重试";
    ElMessage.error(message);
  }

  return Promise.reject(error);
};

service.interceptors.response.use(unwrapResponse, handleResponseError);

export default service;
