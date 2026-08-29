<script setup>
/**
 * 注册页组件。
 *
 * 提供公众用户注册入口，完成账号信息校验与安全强度提示，
 * 作为游客进入旅游信息系统的身份创建流程。
 */
import { computed, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { registerPublicAccount } from "@/api/auth";
import registerBackgroundUrl from "@/assets/images/auth/register-zine.webp";

const router = useRouter();

const loading = ref(false);
const showPassword = ref(false);
const showConfirmPassword = ref(false);
const cardTransform = ref("");

const form = reactive({
  username: "",
  nickname: "",
  password: "",
  confirmPassword: "",
});

const errors = reactive({
  username: "",
  nickname: "",
  password: "",
  confirmPassword: "",
});

const commonPasswords = new Set([
  "12345678",
  "password",
  "password123",
  "qwerty123",
  "admin123",
  "11111111",
]);

/**
 * 计算密码强度等级。
 * @type {import("vue").ComputedRef<{text: string, level: number}>}
 */
const passwordStrength = computed(() => {
  const value = form.password;
  if (!value) return { text: "待评估", level: 0 };
  const groups = [
    /[a-z]/.test(value),
    /[A-Z]/.test(value),
    /\d/.test(value),
    /[^A-Za-z0-9]/.test(value),
  ].filter(Boolean).length;

  if (value.length < 8 || groups < 3) {
    return { text: "弱 (未达到要求)", level: 1 };
  }
  if (groups === 3) return { text: "中 (安全性合格)", level: 2 };
  return { text: "强 (安全性良好)", level: 3 };
});

/**
 * 提交按钮可用性计算。
 * @type {import("vue").ComputedRef<boolean>}
 */
const canSubmit = computed(
  () =>
    !loading.value &&
    form.username.trim() &&
    form.nickname.trim() &&
    form.password.length >= 8 &&
    form.confirmPassword.length >= 8 &&
    !errors.username &&
    !errors.nickname &&
    !errors.password &&
    !errors.confirmPassword,
);

/**
 * 校验注册表单字段并更新错误提示。
 * @param {"username" | "nickname" | "password" | "confirmPassword"} field - 字段名。
 * @returns {void}
 */
const validateField = (field) => {
  if (field === "username") {
    const val = form.username.trim();
    if (!val) {
      errors.username = "请输入账号";
      return;
    }
    errors.username = /^[A-Za-z][A-Za-z0-9_.-]{3,31}$/.test(val)
      ? ""
      : "4–32 位，以字母开头，可包含数字、点、下划线或连字符";
    return;
  }

  if (field === "nickname") {
    const val = form.nickname.trim();
    if (!val) {
      errors.nickname = "请输入公开展示昵称";
      return;
    }
    errors.nickname =
      val.length >= 2 && val.length <= 30
        ? ""
        : "昵称长度须为 2–30 个字符";
    return;
  }

  if (field === "password") {
    if (!form.password) {
      errors.password = "请输入安全密匙";
      return;
    }
    if (form.password.length < 8 || form.password.length > 128) {
      errors.password = "密码长度须为 8–128 位";
    } else {
      const groups = [
        /[a-z]/.test(form.password),
        /[A-Z]/.test(form.password),
        /\d/.test(form.password),
        /[^A-Za-z0-9]/.test(form.password),
      ].filter(Boolean).length;
      const normalizedPassword = form.password.toLowerCase();
      const normalizedUsername = form.username.trim().toLowerCase();
      if (groups < 3) {
        errors.password = "须包含大小写字母、数字、特殊字符中的至少三类";
      } else if (commonPasswords.has(normalizedPassword)) {
        errors.password = "该密码过于常见，请更换更安全的密码";
      } else if (
        normalizedUsername &&
        normalizedPassword.includes(normalizedUsername)
      ) {
        errors.password = "密码不能包含完整账号";
      } else {
        errors.password = "";
      }
    }

    if (form.confirmPassword) validateField("confirmPassword");
    return;
  }

  if (field === "confirmPassword") {
    if (!form.confirmPassword) {
      errors.confirmPassword = "请再次确认密匙";
      return;
    }
    errors.confirmPassword =
      form.confirmPassword !== form.password ? "两次输入的密匙不匹配" : "";
  }
};

/**
 * 计算注册卡片的鼠标视差效果。
 * @param {MouseEvent} event - 鼠标移动事件。
 * @returns {void}
 */
const onCardMove = (event) => {
  const rect = event.currentTarget.getBoundingClientRect();
  const x = (event.clientX - rect.left) / rect.width - 0.5;
  const y = (event.clientY - rect.top) / rect.height - 0.5;
  cardTransform.value = `perspective(1000px) rotateY(${x * 6}deg) rotateX(${y * -6}deg)`;
};

/**
 * 重置注册卡片视差效果。
 * @returns {void}
 */
const resetCard = () => {
  cardTransform.value = "";
};

/**
 * 提交注册请求并导航至登录页。
 * @returns {Promise<void>}
 */
const handleRegister = async () => {
  ["username", "nickname", "password", "confirmPassword"].forEach(validateField);
  if (!canSubmit.value) return;
  loading.value = true;
  try {
    const response = await registerPublicAccount({
      username: form.username.trim(),
      nickname: form.nickname.trim(),
      password: form.password,
    });

    if (response?.code === 201) {
      ElMessage.success("账号创建成功，请登录");
      router.push({ path: "/login", query: { username: response.username } });
    }
  } catch (error) {
    const field = error.response?.data?.field;
    if (field && Object.hasOwn(errors, field)) {
      errors[field] = error.response.data.error;
    }
    ElMessage.error(
      error.response?.data?.error || "注册服务暂不可用，请稍后重试",
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
 * 跳转至登录页。
 * @returns {void}
 */
const goLogin = () => router.push("/login");
</script>

<template>
  <main class="register-page">
    <div
      class="register-bg"
      :style="{ '--auth-background': `url(${registerBackgroundUrl})` }"
    ></div>
    <div class="register-grain"></div>

    <button class="register-back-home" @click="goHome">返回首页</button>

    <section
      class="register-card"
      :style="{ transform: cardTransform }"
      @mousemove="onCardMove"
      @mouseleave="resetCard"
    >
      <div class="register-brand">
        <img
          src="/logo-mark-v2.png"
          alt="Brand Logo"
          width="52"
          height="52"
          loading="eager"
          fetchpriority="high"
          decoding="async"
        />
        <div>
          <h1 class="font-serif">醉美遵义 · 山河红韵</h1>
          <p>开启属于您的黔北深度探索旅程</p>
        </div>
      </div>

      <div class="register-tab-row">
        <button class="register-tab" type="button" @click="goLogin">
          账号登录
        </button>
        <button class="register-tab is-active" type="button">创建新账号</button>
      </div>

      <form class="register-form" @submit.prevent="handleRegister">
        <label class="register-field">
          <span>账 号</span>
          <input
            v-model="form.username"
            type="text"
            placeholder="请输入账号"
            autocomplete="username"
            @blur="validateField('username')"
            @input="validateField('username')"
          />
          <small v-if="errors.username" class="register-error">{{
            errors.username
          }}</small>
        </label>

        <label class="register-field">
          <span>昵称</span>
          <input
            v-model="form.nickname"
            type="text"
            placeholder="请输入用户名（用于平台显示）"
            autocomplete="nickname"
            @blur="validateField('nickname')"
            @input="validateField('nickname')"
          />
          <small v-if="errors.nickname" class="register-error">{{
            errors.nickname
          }}</small>
        </label>

        <label class="register-field">
          <span>密 码</span>
          <div class="register-pw-wrap">
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="请输入密码"
              autocomplete="new-password"
              @blur="validateField('password')"
              @input="validateField('password')"
            />
            <button
              class="register-pw-toggle"
              type="button"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? "隐藏" : "显示" }}
            </button>
          </div>
          <div class="register-pw-meta">
            <small v-if="errors.password" class="register-error">{{
              errors.password
            }}</small>
            <small v-else class="register-hint"
              >强度评级：{{ passwordStrength.text }}</small
            >
            <div class="register-strength-bar">
              <i :class="{ active: passwordStrength.level >= 1 }"></i>
              <i :class="{ active: passwordStrength.level >= 2 }"></i>
              <i :class="{ active: passwordStrength.level >= 3 }"></i>
            </div>
          </div>
        </label>

        <label class="register-field">
          <span>再次确认密码</span>
          <div class="register-pw-wrap">
            <input
              v-model="form.confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              placeholder="请输入密码"
              autocomplete="new-password"
              @blur="validateField('confirmPassword')"
              @input="validateField('confirmPassword')"
            />
            <button
              class="register-pw-toggle"
              type="button"
              @click="showConfirmPassword = !showConfirmPassword"
            >
              {{ showConfirmPassword ? "隐藏" : "显示" }}
            </button>
          </div>
          <small v-if="errors.confirmPassword" class="register-error">{{
            errors.confirmPassword
          }}</small>
        </label>

        <button
          class="register-submit-btn"
          :disabled="!canSubmit"
          type="submit"
        >
          <span v-if="loading" class="register-loading-dot"></span>
          {{ loading ? "正在创建..." : "立即创建账号" }}
        </button>
      </form>

      <p class="register-privacy-tip">
        请勿使用与其他重要网站相同的密码，也不要填写敏感个人信息。
      </p>
    </section>
  </main>
</template>

<style scoped>
.register-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  position: relative;
  overflow: hidden;
  background: #202724;
}

.register-bg {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(125deg, rgba(27, 34, 31, 0.9), rgba(70, 74, 65, 0.68)),
    linear-gradient(35deg, rgba(181, 138, 75, 0.28), transparent 50%),
    var(--auth-background) center / cover no-repeat;
  filter: saturate(1.1) brightness(0.85);
}

.register-grain {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
  background-size: 28px 28px;
  pointer-events: none;
}

.register-back-home {
  position: absolute;
  left: 24px;
  top: 24px;
  z-index: 2;
  height: 42px;
  padding: 0 20px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(8px);
  color: #fff;
  font-size: 14px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.register-back-home:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.4);
}

.register-card {
  width: min(100%, 480px);
  z-index: 1;
  border-radius: 28px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(7, 15, 10, 0.45);
  backdrop-filter: blur(20px) saturate(160%);
  box-shadow: 0 40px 100px rgba(0, 0, 0, 0.45);
  padding: 36px;
  color: #fff;
  transition: transform 0.1s linear;
  will-change: transform;
}

.register-brand {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 24px;
}

.register-brand img {
  width: 52px;
  height: 52px;
  border-radius: 14px;
}

.register-brand h1 {
  margin: 0;
  font-size: 22px;
  letter-spacing: 0.05em;
}

.register-brand p {
  margin: 4px 0 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.65);
}

.register-tab-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 28px;
}

.register-tab {
  height: 44px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  transition: all 0.3s;
}

.register-tab.is-active {
  background: linear-gradient(135deg, #a61f2d, #791722);
  border-color: transparent;
  color: #fff;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(166, 31, 45, 0.3);
}

.register-form {
  display: grid;
  gap: 20px;
}

.register-field {
  display: grid;
  gap: 8px;
}

.register-field span {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  padding-left: 4px;
}

.register-field input {
  height: 48px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.35);
  color: #fff;
  padding: 0 16px;
  outline: none;
  transition: all 0.3s;
}

.register-field input:focus {
  border-color: #b58a4b;
  box-shadow: 0 0 0 4px rgba(181, 138, 75, 0.16);
}

.register-pw-wrap {
  position: relative;
}

.register-pw-wrap input {
  width: 100%;
  padding-right: 74px;
}

.register-pw-toggle {
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
}

.register-pw-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 0 4px;
}

.register-hint {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
}

.register-strength-bar {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
}

.register-strength-bar i {
  display: block;
  height: 4px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.1);
  transition: all 0.4s ease;
}

.register-strength-bar i.active {
  background: #b58a4b;
  box-shadow: 0 0 8px rgba(181, 138, 75, 0.38);
}

.register-error {
  color: #e8a8ad;
  font-size: 12px;
}

.register-submit-btn {
  height: 54px;
  margin-top: 12px;
  border: none;
  border-radius: 14px;
  color: #fff;
  font-weight: 700;
  font-size: 16px;
  background: linear-gradient(135deg, #a61f2d, #791722);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.register-submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  filter: brightness(1.1);
  box-shadow: 0 10px 20px rgba(166, 31, 45, 0.3);
}

.register-submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  filter: grayscale(0.4);
}

.register-loading-dot {
  width: 18px;
  height: 18px;
  border: 3px solid rgba(255, 255, 255, 0.25);
  border-top-color: #fff;
  border-radius: 50%;
  animation: register-spin 0.8s linear infinite;
}

.register-action-row {
  margin-top: 28px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.register-ghost-btn {
  height: 42px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.75);
  font-size: 14px;
  transition: all 0.3s;
}

.register-ghost-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.35);
  color: #fff;
}

.register-privacy-tip {
  margin-top: 24px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.35);
  text-align: center;
  line-height: 1.5;
}

@keyframes register-spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 640px) {
  .register-card {
    border-radius: 20px;
    padding: 24px;
    transform: none !important;
  }
}
</style>
