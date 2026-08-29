/**
 * 前端会话状态。
 *
 * 短期访问令牌仅保存在内存中；页面刷新后通过 HttpOnly Cookie 换取新令牌，
 * 从而避免把长期认证凭据暴露给 JavaScript。
 */

const USER_KEY = "authUser";
let accessToken = "";

const storages = [localStorage, sessionStorage];

export const getToken = () => accessToken;

export const getUserInfo = () => {
  const raw = storages.map((storage) => storage.getItem(USER_KEY)).find(Boolean);
  if (!raw) return null;

  try {
    return JSON.parse(raw);
  } catch {
    clearSession();
    return null;
  }
};

export const saveSession = ({ accessToken: token, user }, persistent = false) => {
  clearSession();
  accessToken = token;
  const storage = persistent ? localStorage : sessionStorage;
  storage.setItem(USER_KEY, JSON.stringify(user));
};

export const clearSession = () => {
  accessToken = "";
  storages.forEach((storage) => {
    storage.removeItem(USER_KEY);
    // 清理旧版本遗留的可持久化访问令牌。
    storage.removeItem("token");
    storage.removeItem("userInfo");
  });
};
