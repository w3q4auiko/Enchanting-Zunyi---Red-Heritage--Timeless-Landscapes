/** 认证 API 与刷新请求去重。 */

import axios from "axios";

import {
  clearSession,
  getToken,
  getUserInfo,
  saveSession,
} from "@/utils/session";

const authClient = axios.create({
  baseURL: "/api",
  timeout: 10000,
  withCredentials: true,
  headers: { "X-Requested-With": "XMLHttpRequest" },
});

let refreshPromise = null;

const applySession = (response) => {
  saveSession(
    { accessToken: response.accessToken, user: response.user },
    response.persistent === true,
  );
  return response;
};

export const loginAccount = async (accountType, credentials) => {
  const endpoint = accountType === "admin" ? "/auth/login" : "/public/login";
  const { data } = await authClient.post(endpoint, credentials);
  return applySession(data);
};

export const registerPublicAccount = async (payload) => {
  const { data } = await authClient.post("/public/register", payload);
  return data;
};

export const refreshSession = (force = false) => {
  if (getToken() && !force) return Promise.resolve(true);
  if (refreshPromise) return refreshPromise;

  refreshPromise = authClient
    .post("/auth/refresh")
    .then(({ data }) => {
      applySession(data);
      return true;
    })
    .catch(() => {
      clearSession();
      return false;
    })
    .finally(() => {
      refreshPromise = null;
    });

  return refreshPromise;
};

export const ensureSession = async () => {
  if (getToken()) return true;
  return refreshSession();
};

export const logoutAccount = async () => {
  try {
    await authClient.post("/auth/logout");
  } catch {
    // 本地退出不依赖网络可用性；服务端会话仍会按有效期自然失效。
  } finally {
    clearSession();
  }
};

export const currentUser = () => getUserInfo();
