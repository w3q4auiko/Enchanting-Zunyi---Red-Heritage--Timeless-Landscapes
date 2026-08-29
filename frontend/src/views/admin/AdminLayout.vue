<script setup>
/**
 * 后台管理统一壳层。
 *
 * 负责品牌导航、页面上下文、移动端侧栏和管理员安全操作，业务页面只关注
 * 各自的数据与表单内容。
 */
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { logoutAccount } from "@/api/auth";
import { getUserInfo } from "@/utils/session";
import {
  ArrowRight,
  Expand,
  Fold,
  Food,
  HomeFilled,
  Location,
  MapLocation,
  Monitor,
  Odometer,
  OfficeBuilding,
  Shop,
  SwitchButton,
  User,
} from "@element-plus/icons-vue";

const router = useRouter();
const route = useRoute();
const userInfo = ref(getUserInfo() || {});
const isCollapse = ref(false);
const mobileMenuOpen = ref(false);
const isCompactScreen = ref(false);

const navSections = [
  {
    label: "工作台",
    items: [
      {
        index: "/admin/dashboard",
        icon: Odometer,
        title: "数据概览",
        description: "运营指标与快捷入口",
      },
    ],
  },
  {
    label: "内容运营",
    items: [
      {
        index: "/admin/attraction",
        icon: Location,
        title: "景点内容",
        description: "景区资料与展示状态",
      },
      {
        index: "/admin/food",
        icon: Food,
        title: "特色美食",
        description: "美食资料与推荐店铺",
      },
      {
        index: "/admin/food-street",
        icon: Shop,
        title: "美食街区",
        description: "街区信息与推荐标签",
      },
      {
        index: "/admin/route",
        icon: MapLocation,
        title: "旅游路线",
        description: "路线资料与用户投稿审核",
      },
      {
        index: "/admin/region",
        icon: OfficeBuilding,
        title: "区域内容",
        description: "区县资料与全域信息",
      },
    ],
  },
  {
    label: "系统管理",
    items: [
      {
        index: "/admin/user",
        icon: User,
        title: "用户管理",
        description: "管理员与普通用户账号",
      },
    ],
  },
];

const menus = navSections.flatMap((section) =>
  section.items.map((item) => ({ ...item, section: section.label })),
);

const activeMenu = computed(() => {
  const matched = menus.find(
    (menu) =>
      route.path === menu.index ||
      (menu.index !== "/admin/dashboard" &&
        route.path.startsWith(`${menu.index}/`)),
  );
  return matched?.index || "/admin/dashboard";
});

const currentPage = computed(() => {
  const matched = menus.find((menu) => menu.index === activeMenu.value);
  if (!matched) {
    return {
      title: "后台管理",
      description: "醉美遵义内容管理中心",
      section: "工作台",
    };
  }

  const action = route.path.includes("/add")
    ? "新增"
    : route.path.includes("/edit/")
      ? "编辑"
      : "";
  return {
    ...matched,
    title: action
      ? `${action}${matched.title.replace("内容", "")}`
      : matched.title,
  };
});

const avatarText = computed(() =>
  (userInfo.value.nickname || userInfo.value.username || "管")
    .charAt(0)
    .toUpperCase(),
);

const updateViewport = () => {
  isCompactScreen.value = window.innerWidth < 960;
  if (!isCompactScreen.value) mobileMenuOpen.value = false;
};

const toggleNavigation = () => {
  if (isCompactScreen.value) {
    mobileMenuOpen.value = !mobileMenuOpen.value;
  } else {
    isCollapse.value = !isCollapse.value;
  }
};

const handleLogout = () => {
  ElMessageBox.confirm("确定退出后台管理中心吗？", "退出确认", {
    confirmButtonText: "安全退出",
    cancelButtonText: "继续工作",
    type: "warning",
    appendTo: document.body,
  })
    .then(async () => {
      await logoutAccount();
      ElMessage.success("已安全退出");
      await router.push("/login");
    })
    .catch(() => {});
};

watch(
  () => route.fullPath,
  () => {
    mobileMenuOpen.value = false;
  },
);

onMounted(() => {
  updateViewport();
  window.addEventListener("resize", updateViewport);
});

onBeforeUnmount(() => window.removeEventListener("resize", updateViewport));
</script>

<template>
  <div
    class="admin-shell"
    :class="{ 'is-collapsed': isCollapse, 'is-mobile-open': mobileMenuOpen }"
  >
    <button
      v-if="mobileMenuOpen"
      class="admin-nav-backdrop"
      aria-label="关闭导航"
      @click="mobileMenuOpen = false"
    />

    <aside class="admin-sidebar">
      <div class="admin-brand" @click="router.push('/admin/dashboard')">
        <div class="admin-brand-mark">
          <img src="/logo-mark-v2.png" alt="山河红韵" width="42" height="42" />
        </div>
        <div v-show="!isCollapse || isCompactScreen" class="admin-brand-copy">
          <strong>山河红韵</strong>
          <span>内容管理中心</span>
        </div>
      </div>

      <nav class="admin-nav" aria-label="后台主导航">
        <section
          v-for="section in navSections"
          :key="section.label"
          class="admin-nav-section"
        >
          <p v-show="!isCollapse || isCompactScreen" class="admin-nav-label">
            {{ section.label }}
          </p>
          <button
            v-for="item in section.items"
            :key="item.index"
            class="admin-nav-item"
            :class="{ 'is-active': activeMenu === item.index }"
            :title="isCollapse && !isCompactScreen ? item.title : undefined"
            @click="router.push(item.index)"
          >
            <el-icon><component :is="item.icon" /></el-icon>
            <span
              v-show="!isCollapse || isCompactScreen"
              class="admin-nav-item-copy"
            >
              <strong>{{ item.title }}</strong>
              <small>{{ item.description }}</small>
            </span>
            <el-icon
              v-show="!isCollapse || isCompactScreen"
              class="admin-nav-arrow"
            >
              <ArrowRight />
            </el-icon>
          </button>
        </section>
      </nav>

      <div class="admin-sidebar-footer">
        <div class="admin-system-dot" />
        <div v-show="!isCollapse || isCompactScreen">
          <strong>系统运行正常</strong>
          <span>认证与数据库服务在线</span>
        </div>
      </div>
    </aside>

    <div class="admin-workspace">
      <header class="admin-topbar">
        <div class="admin-topbar-context">
          <button
            class="admin-icon-button"
            aria-label="切换导航"
            @click="toggleNavigation"
          >
            <el-icon
              ><Expand v-if="isCollapse || isCompactScreen" /><Fold v-else
            /></el-icon>
          </button>
          <div>
            <div class="admin-breadcrumb">
              <span>{{ currentPage.section }}</span>
              <span>/</span>
              <span>{{ currentPage.title }}</span>
            </div>
            <h1>{{ currentPage.title }}</h1>
          </div>
        </div>

        <div class="admin-topbar-actions">
          <el-dropdown trigger="click">
            <div class="admin-profile">
              <el-avatar :size="38">{{ avatarText }}</el-avatar>
              <div class="admin-profile-copy">
                <strong>{{
                  userInfo.nickname || userInfo.username || "管理员"
                }}</strong>
                <span>{{ userInfo.username || "admin" }} · 管理员</span>
              </div>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item :icon="Monitor" @click="router.push('/')">
                  返回网站
                </el-dropdown-item>
                <el-dropdown-item
                  divided
                  :icon="SwitchButton"
                  @click="handleLogout"
                >
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <main class="admin-main">
        <div class="admin-content">
          <router-view v-slot="{ Component }">
            <transition mode="out-in" name="admin-page-fade">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.admin-page-fade-enter-active,
.admin-page-fade-leave-active {
  transition:
    opacity 0.18s ease,
    transform 0.18s ease;
}

.admin-page-fade-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.admin-page-fade-leave-to {
  opacity: 0;
}
</style>
