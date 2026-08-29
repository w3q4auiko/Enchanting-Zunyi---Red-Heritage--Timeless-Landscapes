<script setup>
/**
 * 全局导航头组件。
 *
 * 该组件承担品牌主导航、用户会话状态呈现与移动端菜单控制，
 * 是前台访问入口的统一导航枢纽。
 */
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ensureSession, logoutAccount } from "@/api/auth";
import { getUserInfo } from "@/utils/session";

const router = useRouter();
const route = useRoute();

const userInfo = ref(null);
const isMobileMenuOpen = ref(false);
const isSticky = ref(false);
const isHidden = ref(false);

let lastScrollY = 0;

const navLinks = [
  { name: "首页", path: "/" },
  { name: "红城文脉", path: "/overview" },
  { name: "红城画卷", path: "/highlights" },
  { name: "黔北食韵", path: "/taste" },
  { name: "黔北指南", path: "/guide" },
  { name: "关于我们", path: "/about" },
];

const currentPath = computed(() => route.path.toLowerCase());

/**
 * 依据滚动位置更新导航栏状态。
 * @returns {void}
 */
const handleScroll = () => {
  const y = window.scrollY;
  isSticky.value = y > 40;
  isHidden.value = y > lastScrollY && y > 100 && !isMobileMenuOpen.value;
  lastScrollY = y;
};

/**
 * 同步本地缓存中的登录信息。
 * @returns {void}
 */
const checkLogin = async () => {
  // 访问令牌仅存于内存；页面刷新后应主动使用 HttpOnly Cookie 恢复会话。
  userInfo.value = (await ensureSession()) ? getUserInfo() : null;
};

/**
 * 切换移动端菜单显隐。
 * @returns {void}
 */
const toggleMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
};

/**
 * 关闭移动端菜单。
 * @returns {void}
 */
const closeMenu = () => {
  isMobileMenuOpen.value = false;
};

/**
 * 执行导航跳转并关闭移动菜单。
 * @param {string} path - 路由路径。
 * @returns {void}
 */
const handleNavClick = (path) => {
  setTimeout(() => {
    router.push(path);
    closeMenu();
  }, 150);
};

/**
 * 跳转至登录页并关闭移动菜单。
 * @returns {void}
 */
const goLogin = () => {
  router.push("/login");
  closeMenu();
};

/**
 * 注销会话并回到首页。
 * @returns {void}
 */
const handleLogout = async () => {
  if (!window.confirm("确定要退出登录吗？")) return;
  await logoutAccount();
  userInfo.value = null;
  await router.push("/");
  closeMenu();
};

onMounted(async () => {
  window.addEventListener("scroll", handleScroll);
  await checkLogin();
});

onUnmounted(() => {
  window.removeEventListener("scroll", handleScroll);
});
</script>

<template>
  <header
    class="site-header"
    :class="{
      'fixed-header': isSticky,
      'menu-open': isMobileMenuOpen,
      'header-hidden': isHidden,
    }"
  >
    <div class="header-inner">
      <div class="logo-area">
        <router-link class="logo-link" to="/">
          <img
            class="brand-logo"
            src="/logo-mark-v2.png"
            alt="醉美遵义 · 山河红韵"
            width="46"
            height="46"
            loading="eager"
            fetchpriority="high"
            decoding="async"
          />
          <div class="brand-text">
            <div class="main-title">醉美遵义</div>
            <div class="sub-title-cn">山河红韵</div>
          </div>
        </router-link>
      </div>

      <nav class="desktop-nav">
        <ul>
          <li v-for="link in navLinks" :key="link.path">
            <router-link
              :to="link.path"
              class="nav-link-item"
              :class="{ active: currentPath === link.path }"
            >
              <span class="link-text">{{ link.name }}</span>
            </router-link>
          </li>
        </ul>
      </nav>

      <div class="right-actions">
        <div class="desktop-user-actions">
          <template v-if="userInfo">
            <span class="welcome-text"
              >Hi, {{ userInfo.nickname || userInfo.username || "用户" }}</span
            >
            <button class="action-btn ghost" @click="handleLogout">退出</button>
          </template>
          <template v-else>
            <button class="action-btn solid" @click="goLogin">
              登录 / 注册
            </button>
          </template>
        </div>
        <button class="hamburger-btn" aria-label="切换菜单" @click="toggleMenu">
          <div class="bar top"></div>
          <div class="bar mid"></div>
          <div class="bar bot"></div>
        </button>
      </div>
    </div>

    <div
      class="mobile-drawer-overlay"
      :class="{ open: isMobileMenuOpen }"
      @click="closeMenu"
    ></div>
    <aside class="mobile-drawer" :class="{ open: isMobileMenuOpen }">
      <div class="drawer-header">
        <img
          class="drawer-logo"
          src="/logo-mark-v2.png"
          alt="logo"
          width="36"
          height="36"
          loading="lazy"
          decoding="async"
        />
        <div class="drawer-brand">醉美遵义 · 山河红韵</div>
        <button
          class="drawer-close-btn"
          aria-label="关闭菜单"
          @click="closeMenu"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path
              d="M18 6L6 18M6 6l12 12"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
            />
          </svg>
        </button>
      </div>
      <ul class="drawer-list">
        <li
          v-for="link in navLinks"
          :key="`m-${link.path}`"
          @click="handleNavClick(link.path)"
        >
          <div
            class="drawer-item"
            :class="{ active: currentPath === link.path }"
          >
            {{ link.name }}
          </div>
        </li>
      </ul>
      <div class="drawer-footer">
        <template v-if="userInfo">
          <button class="drawer-btn ghost-red" @click="handleLogout">
            退出登录
          </button>
        </template>
        <template v-else>
          <button class="drawer-btn solid" @click="goLogin">
            立即登录 / 注册
          </button>
        </template>
      </div>
    </aside>
  </header>
</template>

<style scoped>
.site-header {
  --brand-red: var(--zunyi-red);
  --brand-red-dark: var(--zunyi-red-dark);
  --brand-ink: var(--shen-hui-lan);
  --brand-paper: var(--paper-white);
  --brand-cream: var(--paper-deep);
  --brand-muted: var(--text-muted);
  --brand-line: var(--border-soft);
  width: 100%;
  height: 90px;
  background: rgba(252, 250, 245, 0.97);
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
  color: var(--brand-ink);
  border-bottom: 1px solid var(--brand-line);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 28px rgba(31, 41, 51, 0.08);
}

.site-header.header-hidden {
  transform: translateY(-100%);
}

.site-header.fixed-header {
  height: 74px;
  background: rgba(252, 250, 245, 0.91);
  backdrop-filter: blur(18px) saturate(140%);
  box-shadow: 0 10px 32px rgba(31, 41, 51, 0.12);
}

.header-inner {
  max-width: 1440px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  gap: 16px;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--brand-ink);
  text-decoration: none;
  transition: transform 0.3s ease;
}
.logo-link:hover {
  transform: scale(1.02);
}
.logo-link:active {
  transform: scale(0.98);
}

.brand-logo {
  width: 52px;
  height: 52px;
  padding: 4px;
  border: 1px solid rgba(200, 16, 46, 0.12);
  border-radius: 16px;
  object-fit: contain;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 6px 18px rgba(31, 41, 51, 0.08);
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.main-title {
  font-family: "Ma Shan Zheng", serif;
  color: var(--brand-ink);
  font-size: 28px;
  letter-spacing: 2px;
  line-height: 1;
}

.sub-title-cn {
  margin-top: 5px;
  color: var(--brand-red);
  font-size: 12px;
  letter-spacing: 0.22em;
  font-weight: 700;
}

.desktop-nav {
  flex: 1;
  display: flex;
  justify-content: center;
}

.desktop-nav ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  gap: 5px;
}

.nav-link-item {
  position: relative;
  display: inline-flex;
  align-items: center;
  color: #555a55;
  padding: 10px 14px;
  border: 1px solid transparent;
  border-radius: 999px;
  font-family:
    "PingFang SC", "Helvetica Neue", Helvetica, "Hiragino Sans GB",
    "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-decoration: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.nav-link-item:hover {
  color: var(--brand-red);
  background: rgba(200, 16, 46, 0.06);
  border-color: rgba(200, 16, 46, 0.1);
}

.nav-link-item:active {
  transform: scale(0.96);
  background: rgba(200, 16, 46, 0.1);
}

.nav-link-item::after {
  display: none;
}

.nav-link-item:hover::after,
.nav-link-item.active::after {
  width: 70%;
  opacity: 1;
}

.nav-link-item.active {
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  background: var(--brand-red);
  border-color: var(--brand-red);
  box-shadow: 0 6px 16px rgba(200, 16, 46, 0.2);
}

.right-actions,
.desktop-user-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.welcome-text {
  font-size: 14px;
  color: var(--brand-muted);
  white-space: nowrap;
}

.action-btn {
  height: 36px;
  padding: 0 16px;
  border-radius: 999px;
  border: 1px solid var(--brand-line);
  background: rgba(255, 255, 255, 0.55);
  color: var(--brand-ink);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
  font-weight: 500;
}

.action-btn.solid {
  background: var(--brand-red);
  border-color: var(--brand-red);
  color: #fff;
  box-shadow: 0 6px 16px rgba(200, 16, 46, 0.18);
}

.action-btn:hover {
  background: var(--brand-ink);
  border-color: var(--brand-ink);
  color: #fff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.action-btn:active {
  transform: translateY(0) scale(0.95);
}

.hamburger-btn {
  display: none;
  width: 32px;
  height: 24px;
  flex-direction: column;
  justify-content: space-between;
  border: none;
  background: none;
  padding: 0;
  cursor: pointer;
}

.hamburger-btn .bar {
  width: 100%;
  height: 2.5px;
  background: var(--brand-ink);
  border-radius: 2px;
  transition: all 0.3s ease;
}

.menu-open .hamburger-btn .top {
  transform: translateY(10.5px) rotate(45deg);
}

.menu-open .hamburger-btn .mid {
  opacity: 0;
  transform: translateX(-20px);
}

.menu-open .hamburger-btn .bot {
  transform: translateY(-10.5px) rotate(-45deg);
}

.mobile-drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(20, 27, 34, 0.58);
  backdrop-filter: blur(4px);
  z-index: 998;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.mobile-drawer-overlay.open {
  opacity: 1;
  visibility: visible;
}

.mobile-drawer {
  position: fixed;
  top: 0;
  right: -320px;
  width: 320px;
  height: 100vh;
  background: var(--brand-paper);
  color: var(--brand-ink);
  z-index: 999;
  display: flex;
  flex-direction: column;
  transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: -10px 0 30px rgba(0, 0, 0, 0.18);
}

.mobile-drawer.open {
  right: 0;
}

.drawer-header {
  background: rgba(255, 255, 255, 0.68);
  color: var(--brand-ink);
  min-height: 88px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px;
  border-bottom: 1px solid var(--brand-line);
}

.drawer-logo {
  width: 44px;
  height: 44px;
  padding: 3px;
  border: 1px solid rgba(200, 16, 46, 0.12);
  border-radius: 13px;
  background: #fff;
}

.drawer-brand {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 1px;
}

.drawer-close-btn {
  margin-left: auto;
  width: 38px;
  height: 38px;
  border-radius: 10px;
  border: 1px solid var(--brand-line);
  background: var(--brand-cream);
  color: var(--brand-ink);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.drawer-close-btn:active {
  transform: scale(0.9);
  background: rgba(200, 16, 46, 0.08);
}

.drawer-list {
  list-style: none;
  margin: 0;
  padding: 12px 0;
  flex: 1;
  overflow-y: auto;
}

.drawer-item {
  padding: 16px 24px;
  font-family:
    "PingFang SC", "Helvetica Neue", Helvetica, "Hiragino Sans GB",
    "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: 1px;
  border-left: 4px solid transparent;
  color: #555a55;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.drawer-item:active {
  background-color: rgba(200, 16, 46, 0.05);
  transform: translateX(6px);
  color: var(--brand-red);
}

.drawer-item.active {
  font-size: 16px;
  font-weight: 700;
  border-left: 5px solid var(--brand-red);
  background: rgba(200, 16, 46, 0.07);
  color: var(--brand-red);
}

.drawer-footer {
  border-top: 1px solid var(--brand-line);
  padding: 20px;
  background: var(--brand-cream);
}

.drawer-btn {
  width: 100%;
  height: 44px;
  border-radius: 10px;
  border: 1px solid #d1d5db;
  background: #fff;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.drawer-btn:active {
  transform: scale(0.96);
}

.drawer-btn.solid {
  background: var(--brand-red);
  border-color: var(--brand-red);
  color: #fff;
}

.drawer-btn.ghost-red {
  color: var(--brand-red);
  border-color: #d9a9ad;
  background: #f8ecec;
}

@media (max-width: 1200px) {
  .desktop-nav,
  .desktop-user-actions {
    display: none;
  }

  .hamburger-btn {
    display: flex;
  }

  .main-title {
    font-size: 26px;
  }
}

@media (max-width: 640px) {
  .site-header {
    height: 76px;
  }

  .site-header.fixed-header {
    height: 68px;
  }

  .header-inner {
    padding: 0 14px;
  }

  .brand-logo {
    width: 42px;
    height: 42px;
    padding: 3px;
    border-radius: 12px;
  }

  .main-title {
    font-size: 22px;
  }

  .sub-title-cn {
    font-size: 11px;
    letter-spacing: 1px;
  }
}
</style>
