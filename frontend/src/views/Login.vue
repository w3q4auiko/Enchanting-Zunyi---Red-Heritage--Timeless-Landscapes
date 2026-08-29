<script setup>
/**
 * 登录页组件。
 *
 * 提供后台与公众用户的统一登录入口，完成身份校验、
 * 会话令牌存储与角色分流。
 */
import { computed, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { loginAccount } from "@/api/auth";
import loginBackgroundUrl from "@/assets/images/auth/login-zine.webp";

const router = useRouter();
const route = useRoute();

const loading = ref(false);
const rememberMe = ref(true);
const showPassword = ref(false);
const cardTransform = ref("");

const form = reactive({
  accountType: "public",
  username: typeof route.query.username === "string" ? route.query.username : "",
  password: "",
});

const errors = reactive({
  username: "",
  password: "",
});

/**
 * 提交按钮可用性计算。
 * @type {import("vue").ComputedRef<boolean>}
 */
const canSubmit = computed(
  () =>
    !loading.value &&
    form.username.trim().length > 0 &&
    form.password.length > 0 &&
    !errors.username &&
    !errors.password,
);

/**
 * 校验表单字段并更新错误提示。
 * @param {"username" | "password"} field - 字段名。
 * @returns {void}
 */
const validateField = (field) => {
  if (field === "username") {
    const username = form.username.trim();
    if (!username) {
      errors.username = "请输入账号";
      return;
    }
    errors.username = username.length <= 64 ? "" : "账号长度不能超过 64 位";
    return;
  }
  if (field === "password") {
    if (!form.password) {
      errors.password = "请输入密码";
      return;
    }
    errors.password =
      form.password.length > 128 ? "密码长度不能超过 128 位" : "";
  }
};

/**
 * 计算登录卡片的鼠标视差效果。
 * @param {MouseEvent} event - 鼠标移动事件。
 * @returns {void}
 */
const onCardMove = (event) => {
  const rect = event.currentTarget.getBoundingClientRect();
  const x = (event.clientX - rect.left) / rect.width - 0.5;
  const y = (event.clientY - rect.top) / rect.height - 0.5;

  cardTransform.value = `perspective(900px) rotateY(${x * 5}deg) rotateX(${y * -5}deg)`;
};

/**
 * 重置卡片视差效果。
 * @returns {void}
 */
const resetCard = () => {
  cardTransform.value = "";
};

/**
 * 统一处理登录成功后的会话写入与跳转。
 * @param {object} res - 登录响应对象。
 * @returns {void}
 */
const handleLoginSuccess = (res) => {
  const userData = res?.user;
  if (!res?.accessToken || !userData) {
    ElMessage.error("登录响应不完整，请稍后重试");
    return;
  }
  ElMessage.success(`欢迎回来，${userData.nickname || userData.username}`);

  const requestedPath =
    typeof route.query.redirect === "string" ? route.query.redirect : "";
  const isSafeLocalPath =
    requestedPath.startsWith("/") && !requestedPath.startsWith("//");
  const target =
    userData.accountType === "admin"
      ? isSafeLocalPath && requestedPath.startsWith("/admin")
        ? requestedPath
        : "/admin/dashboard"
      : isSafeLocalPath && !requestedPath.startsWith("/admin")
        ? requestedPath
        : "/";
  router.replace(target);
};

/**
 * 提交登录请求并处理角色分流。
 * @returns {Promise<void>}
 */
const handleLogin = async () => {
  validateField("username");
  validateField("password");
  if (!canSubmit.value) return;
  loading.value = true;

  try {
    const responseData = await loginAccount(form.accountType, {
      username: form.username.trim(),
      password: form.password,
      remember: rememberMe.value,
    });

    if (responseData?.code === 200) {
      handleLoginSuccess(responseData);
      return;
    }
    ElMessage.error(responseData?.msg || "账号识别码或密匙错误");
  } catch (error) {
    const field = error.response?.data?.field;
    if (field && Object.hasOwn(errors, field)) {
      errors[field] = error.response.data.error;
    }
    ElMessage.error(
      error.response?.data?.error || "登录服务暂不可用，请稍后重试",
    );
  } finally {
    loading.value = false;
  }
};

/**
 * 跳转至首页。
 * @returns {void}
 */
const goHome = () => router.push("/");

/**
 * 跳转至注册页。
 * @returns {void}
 */
const goRegister = () => router.push("/register");
</script>

<template>
  <main class="login-page">
    <div
      class="login-bg"
      :style="{ '--auth-background': `url(${loginBackgroundUrl})` }"
    ></div>
    <div class="login-grain"></div>

    <button class="login-back-home" @click="goHome">返回首页</button>

    <section
      class="login-card"
      :style="{ transform: cardTransform }"
      @mousemove="onCardMove"
      @mouseleave="resetCard"
    >
      <div class="login-brand">
        <img
          src="/logo-mark-v2.png"
          alt="Logo"
          width="54"
          height="54"
          loading="eager"
          fetchpriority="high"
          decoding="async"
        />
        <div>
          <h1 class="font-serif">醉美遵义 · 山河红韵</h1>
        </div>
      </div>

      <div class="login-tab-row">
        <button class="login-tab is-active" type="button">登录账户</button>
        <button class="login-tab" type="button" @click="goRegister">
          新用户注册
        </button>
      </div>

      <form class="login-form" @submit.prevent="handleLogin">
        <fieldset class="login-role-switch">
          <legend>登录身份</legend>
          <label :class="{ active: form.accountType === 'public' }">
            <input v-model="form.accountType" type="radio" value="public" />
            普通用户
          </label>
          <label :class="{ active: form.accountType === 'admin' }">
            <input v-model="form.accountType" type="radio" value="admin" />
            管理员
          </label>
        </fieldset>

        <label class="login-field">
          <span>账 号</span>
          <input
            v-model="form.username"
            type="text"
            placeholder="请输入账号"
            autocomplete="username"
            @blur="validateField('username')"
            @input="validateField('username')"
          />
          <transition name="fade">
            <small v-if="errors.username" class="login-error">{{
              errors.username
            }}</small>
          </transition>
        </label>

        <label class="login-field">
          <span>密 码</span>
          <div class="login-pw-wrap">
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="请输入密码"
              autocomplete="current-password"
              @blur="validateField('password')"
              @input="validateField('password')"
            />
            <button
              class="login-pw-toggle"
              type="button"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? "隐藏" : "显示" }}
            </button>
          </div>
          <transition name="fade">
            <small v-if="errors.password" class="login-error">{{
              errors.password
            }}</small>
          </transition>
        </label>

        <div class="login-row">
          <label class="login-checkbox">
            <input v-model="rememberMe" type="checkbox" />
            <span>自动保持登录状态</span>
          </label>
        </div>

        <button class="login-submit-btn" :disabled="!canSubmit" type="submit">
          <span v-if="loading" class="login-loading-dot"></span>
          {{ loading ? "正在验证..." : "登录" }}
        </button>
      </form>

      <p class="login-privacy-tip">请仅在可信设备上保持登录，并在使用后及时退出。</p>
    </section>
  </main>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  position: relative;
  overflow: hidden;
  background: #202724;
}

.login-bg {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(120deg, rgba(27, 34, 31, 0.9), rgba(93, 18, 27, 0.66)),
    linear-gradient(20deg, rgba(166, 31, 45, 0.28), transparent 45%),
    var(--auth-background) center / cover no-repeat;
  filter: brightness(0.8);
}

.login-grain {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
  background-size: 24px 24px;
  pointer-events: none;
}

.login-back-home {
  position: absolute;
  left: 24px;
  top: 24px;
  z-index: 2;
  height: 42px;
  padding: 0 20px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(4px);
  color: #fff;
  font-size: 14px;
  transition: all 0.3s;
}

.login-back-home:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.4);
}

.login-card {
  width: min(100%, 470px);
  z-index: 1;
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: rgba(15, 8, 8, 0.45);
  backdrop-filter: blur(20px) saturate(180%);
  box-shadow: 0 40px 100px rgba(0, 0, 0, 0.4);
  padding: 32px;
  color: #fff;
  transition: transform 0.1s linear;
  will-change: transform;
}

.login-brand {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 24px;
}

.login-brand img {
  width: 54px;
  height: 54px;
  border-radius: 14px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.login-brand h1 {
  margin: 0;
  font-size: 22px;
  letter-spacing: 0.05em;
}

.login-brand p {
  margin: 4px 0 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.login-tab-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 24px;
}

.login-tab {
  height: 44px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  transition: all 0.3s;
}

.login-tab.is-active {
  background: linear-gradient(135deg, #a61f2d, #791722);
  border-color: transparent;
  color: #fff;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(166, 31, 45, 0.3);
}

.login-form {
  display: grid;
  gap: 18px;
}

.login-role-switch {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin: 0;
  padding: 0;
  border: 0;
}

.login-role-switch legend {
  grid-column: 1 / -1;
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
}

.login-role-switch label {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 40px;
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.65);
  cursor: pointer;
}

.login-role-switch label.active {
  border-color: #b58a4b;
  background: rgba(181, 138, 75, 0.13);
  color: #fff;
}

.login-field {
  display: grid;
  gap: 8px;
}

.login-field span {
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
  padding-left: 4px;
}

.login-field input {
  height: 48px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.3);
  color: #fff;
  padding: 0 16px;
  outline: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.login-field input:focus {
  border-color: #b58a4b;
  background: rgba(0, 0, 0, 0.5);
  box-shadow: 0 0 0 4px rgba(181, 138, 75, 0.16);
}

.login-pw-wrap {
  position: relative;
}

.login-pw-wrap input {
  width: 100%;
  padding-right: 74px;
}

.login-pw-toggle {
  position: absolute;
  top: 50%;
  right: 10px;
  transform: translateY(-50%);
  height: 28px;
  padding: 0 12px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.6);
  font-size: 11px;
  transition: all 0.2s;
}

.login-pw-toggle:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
}

.login-error {
  color: #e8a8ad;
  font-size: 12px;
  padding-left: 4px;
}

.login-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.login-checkbox {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
}

.login-text-btn {
  border: none;
  background: none;
  color: #b58a4b;
  font-size: 13px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.login-text-btn:hover {
  text-decoration: underline;
  opacity: 0.8;
}

.login-submit-btn {
  height: 52px;
  margin-top: 10px;
  border: none;
  border-radius: 12px;
  color: #fff;
  font-weight: 700;
  font-size: 16px;
  background: linear-gradient(135deg, #a61f2d, #791722);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.login-submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(166, 31, 45, 0.36);
}

.login-submit-btn:disabled {
  opacity: 0.5;
  filter: grayscale(0.5);
  cursor: not-allowed;
}

.login-loading-dot {
  width: 18px;
  height: 18px;
  border: 3px solid rgba(255, 255, 255, 0.2);
  border-top-color: #fff;
  border-radius: 50%;
  animation: login-spin 0.8s cubic-bezier(0.6, 0.2, 0.4, 0.8) infinite;
}

.login-action-row {
  margin-top: 24px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.ghost-btn {
  height: 42px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.03);
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  transition: all 0.3s;
}

.ghost-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
  color: #fff;
}

.login-privacy-tip {
  margin-top: 20px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  text-align: center;
  line-height: 1.6;
}

@keyframes login-spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 640px) {
  .login-card {
    border-radius: 20px;
    padding: 24px;
    transform: none !important;
  }
}
</style>
