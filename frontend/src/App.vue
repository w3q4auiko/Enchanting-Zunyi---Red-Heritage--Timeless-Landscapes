<script setup>
/**
 * 应用根布局组件。
 *
 * 该组件作为前端视图装配入口，统一挂载全局头尾布局、
 * 以及与投稿入口和返回顶部相关的全局交互能力。
 */
import { onMounted, onUnmounted, ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import Header from "./components/Header.vue";
import Footer from "./components/Footer.vue";

const router = useRouter();
const route = useRoute();

const showBackToTop = ref(false);

/**
 * 监听滚动位置以控制悬浮操作按钮显示状态。
 * @returns {void}
 */
const handleScroll = () => {
  showBackToTop.value = window.scrollY > 300;
};

/**
 * 平滑滚动至页面顶部。
 * @returns {void}
 */
const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: "smooth" });
};

/**
 * 跳转至用户投稿入口。
 * @returns {void}
 */
const goContribute = () => {
  router.push("/user/contribute");
};

onMounted(() => {
  window.addEventListener("scroll", handleScroll);
});

onUnmounted(() => {
  window.removeEventListener("scroll", handleScroll);
});
</script>

<template>
  <div class="app-container">
    <Header v-if="!route.meta.hideLayout" />

    <div :class="route.meta.hideLayout ? '' : 'main-body'">
      <router-view />
    </div>

    <Footer v-if="!route.meta.hideLayout" />
  </div>

  <div v-if="!route.meta.hideLayout" class="floating-group">
    <div
      :class="{ show: showBackToTop }"
      class="float-btn back-top-btn"
      @click="goContribute"
    >
      <svg
        class="icon"
        fill="none"
        stroke="currentColor"
        stroke-width="2.5"
        viewBox="0 0 24 24"
      >
        <path
          d="M12 4v16m8-8H4"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
      <span class="tooltip-text">我要投稿</span>
    </div>

    <div
      :class="{ show: showBackToTop }"
      class="float-btn back-top-btn"
      @click="scrollToTop"
    >
      <svg
        class="icon"
        fill="none"
        stroke="currentColor"
        stroke-width="2.5"
        viewBox="0 0 24 24"
      >
        <path
          d="M5 10l7-7m0 0l7 7m-7-7v18"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
      <span class="tooltip-text">回到顶部</span>
    </div>
  </div>
</template>

<style>
body {
  margin: 0;
  padding: 0;
  font-family:
    "PingFang SC", "Helvetica Neue", Helvetica, "Hiragino Sans GB",
    "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: var(--qian-mi-bai);
  color: var(--zheng-wen);
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-body {
  flex: 1;
  margin-top: 90px;
}

@media screen and (max-width: 640px) {
  .main-body {
    margin-top: 76px !important;
  }
}

.floating-group {
  position: fixed;
  bottom: 30px;
  right: 30px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 999;
  align-items: flex-end;
}

.float-btn {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(252, 250, 245, 0.92);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid var(--border-soft);
  box-shadow: 0 4px 15px rgba(55, 45, 35, 0.1);
  color: var(--shen-hui-lan);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.float-btn .icon {
  width: 22px;
  height: 22px;
  transition: transform 0.3s ease;
}

.float-btn:hover {
  background: var(--zunyi-red);
  color: white;
  border-color: transparent;
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(166, 31, 45, 0.28);
}

.float-btn:hover .icon {
  transform: scale(1.1);
}

.tooltip-text {
  position: absolute;
  right: 60px;
  top: 50%;
  transform: translateY(-50%) translateX(10px);
  background: rgba(32, 39, 36, 0.9);
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.tooltip-text::after {
  content: "";
  position: absolute;
  right: -4px;
  top: 50%;
  transform: translateY(-50%);
  border-width: 4px 0 4px 4px;
  border-style: solid;
  border-color: transparent transparent transparent rgba(32, 39, 36, 0.9);
}

.float-btn:hover .tooltip-text {
  opacity: 1;
  visibility: visible;
  transform: translateY(-50%) translateX(0);
}

.back-top-btn {
  opacity: 0;
  visibility: hidden;
  transform: translateY(20px) scale(0.8);
  pointer-events: none;
}

.back-top-btn.show {
  opacity: 1;
  visibility: visible;
  transform: translateY(0) scale(1);
  pointer-events: auto;
}

.back-top-btn.show:hover {
  transform: translateY(-3px) scale(1);
}
</style>
