<script setup>
/** 后台运营概览：展示真实资源规模、内容入口与维护提醒。 */
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import request from "@/utils/request";
import {
  ArrowRight,
  Bell,
  DataBoard,
  Food,
  Location,
  OfficeBuilding,
  Plus,
  Shop,
  Ticket,
  User,
} from "@element-plus/icons-vue";

const router = useRouter();
const loading = ref(false);
const stats = ref({
  admin_count: 0,
  public_user_count: 0,
  attraction_count: 0,
  food_count: 0,
  food_street_count: 0,
  region_count: 0,
  route_count: 0,
});

const fetchStats = async () => {
  loading.value = true;
  try {
    const res = await request.get("/admin/stats");
    const data = res.data || res;
    stats.value = {
      admin_count: data.admin_count ?? data.user_count ?? 0,
      public_user_count: data.public_user_count ?? 0,
      attraction_count: data.attraction_count ?? 0,
      food_count: data.food_count ?? 0,
      food_street_count: data.food_street_count ?? 0,
      region_count: data.region_count ?? 0,
      route_count: data.route_count ?? 0,
    };
  } catch (error) {
    console.error("Failed to fetch dashboard stats:", error);
  } finally {
    loading.value = false;
  }
};

const greeting = computed(() => {
  const hour = new Date().getHours();
  if (hour < 6) return "夜深了，注意休息";
  if (hour < 9) return "早上好，开始今天的内容巡检";
  if (hour < 12) return "上午好，欢迎回到管理中心";
  if (hour < 14) return "中午好，记得适当休息";
  if (hour < 18) return "下午好，继续完善遵义文旅内容";
  return "晚上好，辛苦了";
});

const today = computed(() =>
  new Intl.DateTimeFormat("zh-CN", {
    month: "long",
    day: "numeric",
    weekday: "long",
  }).format(new Date()),
);

const statCards = computed(() => [
  { label: "景点内容", value: stats.value.attraction_count, icon: Ticket, tone: "red" },
  { label: "特色美食", value: stats.value.food_count, icon: Food, tone: "orange" },
  { label: "美食街区", value: stats.value.food_street_count, icon: Shop, tone: "teal" },
  { label: "区域资料", value: stats.value.region_count, icon: OfficeBuilding, tone: "blue" },
  { label: "旅游路线", value: stats.value.route_count, icon: Location, tone: "teal" },
  { label: "注册用户", value: stats.value.public_user_count, icon: User, tone: "violet" },
  { label: "管理员", value: stats.value.admin_count, icon: DataBoard, tone: "slate" },
]);

const contentTotal = computed(
  () =>
    stats.value.attraction_count +
    stats.value.food_count +
    stats.value.food_street_count +
    stats.value.region_count +
    stats.value.route_count,
);

const quickActions = [
  {
    title: "发布景点",
    description: "新增景区资料与服务信息",
    icon: Location,
    path: "/admin/attraction/add",
  },
  {
    title: "新增美食",
    description: "维护菜品、店铺与推荐内容",
    icon: Food,
    path: "/admin/food/add",
  },
  {
    title: "维护街区",
    description: "管理街区资料与推荐标签",
    icon: Shop,
    path: "/admin/food-street",
  },
  {
    title: "管理区域",
    description: "更新区县概况和展示状态",
    icon: OfficeBuilding,
    path: "/admin/region",
  },
];

onMounted(fetchStats);
</script>

<template>
  <div class="admin-page dashboard-page">
    <section class="dashboard-hero">
      <div class="dashboard-hero-copy">
        <span class="dashboard-date">{{ today }}</span>
        <h2>{{ greeting }}</h2>
        <p>集中维护红色文化、山水景区与遵义味道，让每一条内容准确、清晰、可信。</p>
        <div class="dashboard-hero-actions">
          <el-button type="primary" :icon="Plus" @click="router.push('/admin/attraction/add')">
            发布内容
          </el-button>
          <button class="dashboard-text-link" @click="router.push('/')">
            查看前台展示 <el-icon><ArrowRight /></el-icon>
          </button>
        </div>
      </div>
      <div class="dashboard-hero-summary">
        <span>已收录内容</span>
        <strong>{{ contentTotal }}</strong>
        <small>条文旅资源</small>
        <DataBoard />
      </div>
    </section>

    <section class="dashboard-section">
      <div class="dashboard-section-heading">
        <div>
          <span>DATA OVERVIEW</span>
          <h3>资源数据概览</h3>
        </div>
        <button class="dashboard-refresh" :disabled="loading" @click="fetchStats">
          {{ loading ? "正在更新…" : "刷新数据" }}
        </button>
      </div>

      <div class="dashboard-stat-grid" v-loading="loading">
        <article v-for="card in statCards" :key="card.label" class="dashboard-stat-card">
          <div class="dashboard-stat-icon" :class="`is-${card.tone}`">
            <el-icon><component :is="card.icon" /></el-icon>
          </div>
          <div>
            <span>{{ card.label }}</span>
            <strong>{{ card.value }}</strong>
          </div>
          <div class="dashboard-stat-rule" :class="`is-${card.tone}`" />
        </article>
      </div>
    </section>

    <div class="dashboard-bottom-grid">
      <section class="admin-panel dashboard-quick-panel">
        <div class="dashboard-section-heading is-compact">
          <div>
            <span>QUICK ACCESS</span>
            <h3>快捷工作入口</h3>
          </div>
        </div>
        <div class="dashboard-action-list">
          <button
            v-for="action in quickActions"
            :key="action.path"
            class="dashboard-action-item"
            @click="router.push(action.path)"
          >
            <span class="dashboard-action-icon">
              <el-icon><component :is="action.icon" /></el-icon>
            </span>
            <span class="dashboard-action-copy">
              <strong>{{ action.title }}</strong>
              <small>{{ action.description }}</small>
            </span>
            <el-icon class="dashboard-action-arrow"><ArrowRight /></el-icon>
          </button>
        </div>
      </section>

      <section class="admin-panel dashboard-notice-panel">
        <div class="dashboard-section-heading is-compact">
          <div>
            <span>OPERATIONS</span>
            <h3>今日维护建议</h3>
          </div>
          <el-icon class="dashboard-notice-bell"><Bell /></el-icon>
        </div>
        <div class="dashboard-notices">
          <article>
            <span class="is-security">安全</span>
            <div>
              <strong>管理员账号已完成清理</strong>
              <p>建议定期检查账号列表，并为在用账号设置独立强密码。</p>
            </div>
          </article>
          <article>
            <span class="is-content">内容</span>
            <div>
              <strong>核对首页重点展示内容</strong>
              <p>发布后请返回前台确认图片、标题和移动端排版。</p>
            </div>
          </article>
          <article>
            <span class="is-backup">备份</span>
            <div>
              <strong>保持数据库备份可恢复</strong>
              <p>重要批量调整前先完成备份，并记录本次修改范围。</p>
            </div>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.dashboard-hero {
  min-height: 238px;
  padding: 34px 38px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 36px;
  color: #fff;
  background:
    radial-gradient(circle at 82% 16%, rgba(181, 138, 75, 0.34), transparent 24%),
    linear-gradient(118deg, #791722 0%, #a61f2d 54%, #303733 54.2%, #202724 100%);
  border-radius: 18px;
  box-shadow: 0 18px 40px rgba(84, 25, 31, 0.18);
  overflow: hidden;
}

.dashboard-hero-copy {
  position: relative;
  z-index: 1;
  max-width: 690px;
}

.dashboard-date,
.dashboard-section-heading span {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.16em;
}

.dashboard-date {
  color: #ead7b8;
}

.dashboard-hero h2 {
  margin: 10px 0 8px;
  font-size: clamp(25px, 2.3vw, 34px);
  line-height: 1.24;
  font-weight: 780;
}

.dashboard-hero p {
  max-width: 620px;
  color: rgba(255, 255, 255, 0.76);
  font-size: 13px;
  line-height: 1.8;
}

.dashboard-hero-actions {
  margin-top: 22px;
  display: flex;
  align-items: center;
  gap: 18px;
}

.dashboard-hero :deep(.el-button--primary) {
  --el-button-bg-color: #fff;
  --el-button-border-color: #fff;
  --el-button-text-color: #8d1b28;
  --el-button-hover-bg-color: #f3e8df;
  --el-button-hover-border-color: #f3e8df;
  --el-button-hover-text-color: #791722;
}

.dashboard-text-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: rgba(255, 255, 255, 0.84);
  background: transparent;
  border: 0;
  cursor: pointer;
}

.dashboard-hero-summary {
  position: relative;
  width: 220px;
  height: 154px;
  flex: 0 0 220px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.13);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  overflow: hidden;
}

.dashboard-hero-summary span,
.dashboard-hero-summary small {
  color: #d8d0c4;
  font-size: 11px;
}

.dashboard-hero-summary strong {
  margin: 5px 0 1px;
  font-size: 42px;
  line-height: 1;
}

.dashboard-hero-summary > svg {
  position: absolute;
  right: -18px;
  bottom: -22px;
  width: 100px;
  height: 100px;
  color: rgba(255, 255, 255, 0.06);
}

.dashboard-section {
  padding: 2px 0;
}

.dashboard-section-heading {
  margin-bottom: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.dashboard-section-heading span {
  color: #a61f2d;
}

.dashboard-section-heading h3 {
  margin: 3px 0 0;
  color: #29312e;
  font-size: 18px;
}

.dashboard-refresh {
  color: #746f67;
  background: transparent;
  border: 0;
  cursor: pointer;
}

.dashboard-stat-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 14px;
}

.dashboard-stat-card {
  position: relative;
  min-height: 126px;
  padding: 19px;
  display: flex;
  align-items: center;
  gap: 14px;
  background: #fcfaf5;
  border: 1px solid #ded4c5;
  border-radius: 14px;
  box-shadow: 0 7px 20px rgba(55, 45, 35, 0.05);
  overflow: hidden;
}

.dashboard-stat-icon {
  width: 43px;
  height: 43px;
  flex: 0 0 43px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  font-size: 19px;
}

.dashboard-stat-card > div:nth-child(2) {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.dashboard-stat-card span {
  color: #746f67;
  font-size: 11px;
  white-space: nowrap;
}

.dashboard-stat-card strong {
  margin-top: 5px;
  color: #29312e;
  font-size: 25px;
}

.dashboard-stat-rule {
  position: absolute;
  inset: auto 0 0;
  height: 3px;
}

.is-red { color: #a61f2d; background: #f8e9e9; }
.is-orange { color: #9e743a; background: #f8efdf; }
.is-teal { color: #586a54; background: #eaf0e7; }
.is-blue { color: #46524c; background: #e9eeeb; }
.is-violet { color: #84505a; background: #f3e9ea; }
.is-slate { color: #5f615d; background: #eee9e1; }
.dashboard-stat-rule.is-red { background: #a61f2d; }
.dashboard-stat-rule.is-orange { background: #b58a4b; }
.dashboard-stat-rule.is-teal { background: #687565; }
.dashboard-stat-rule.is-blue { background: #46524c; }
.dashboard-stat-rule.is-violet { background: #84505a; }
.dashboard-stat-rule.is-slate { background: #746f67; }

.dashboard-bottom-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(340px, 0.65fr);
  gap: 20px;
}

.dashboard-quick-panel,
.dashboard-notice-panel {
  padding: 24px;
}

.dashboard-section-heading.is-compact {
  margin-bottom: 18px;
}

.dashboard-action-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.dashboard-action-item {
  min-height: 82px;
  padding: 14px;
  display: flex;
  align-items: center;
  gap: 12px;
  text-align: left;
  background: #faf7f1;
  border: 1px solid #e5dccf;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.18s ease;
}

.dashboard-action-item:hover {
  background: #f8eeee;
  border-color: #d9a9ad;
  transform: translateY(-1px);
}

.dashboard-action-icon {
  width: 40px;
  height: 40px;
  flex: 0 0 40px;
  display: grid;
  place-items: center;
  color: #a61f2d;
  background: #f8e9e9;
  border-radius: 11px;
}

.dashboard-action-copy {
  min-width: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.dashboard-action-copy strong {
  color: #29312e;
  font-size: 13px;
}

.dashboard-action-copy small {
  margin-top: 4px;
  overflow: hidden;
  color: #746f67;
  font-size: 10px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dashboard-action-arrow {
  color: #a39788;
}

.dashboard-notice-bell {
  color: #a61f2d;
  font-size: 20px;
}

.dashboard-notices {
  display: flex;
  flex-direction: column;
}

.dashboard-notices article {
  padding: 13px 0;
  display: flex;
  align-items: flex-start;
  gap: 11px;
  border-top: 1px solid #e5dccf;
}

.dashboard-notices article:first-child {
  padding-top: 0;
  border-top: 0;
}

.dashboard-notices article > span {
  padding: 4px 7px;
  flex: 0 0 auto;
  font-size: 9px;
  font-weight: 800;
  border-radius: 6px;
}

.dashboard-notices .is-security { color: #a61f2d; background: #f8e9e9; }
.dashboard-notices .is-content { color: #586a54; background: #eaf0e7; }
.dashboard-notices .is-backup { color: #9e743a; background: #f8efdf; }

.dashboard-notices strong {
  color: #29312e;
  font-size: 12px;
}

.dashboard-notices p {
  margin-top: 4px;
  color: #746f67;
  font-size: 10px;
  line-height: 1.55;
}

@media (max-width: 1320px) {
  .dashboard-stat-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}

@media (max-width: 900px) {
  .dashboard-hero { background: linear-gradient(135deg, #791722, #a61f2d); }
  .dashboard-hero-summary { display: none; }
  .dashboard-bottom-grid { grid-template-columns: 1fr; }
}

@media (max-width: 640px) {
  .dashboard-page { gap: 18px; }
  .dashboard-hero { min-height: 0; padding: 26px 22px; }
  .dashboard-stat-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .dashboard-stat-card { min-height: 105px; padding: 14px; }
  .dashboard-stat-icon { width: 36px; height: 36px; flex-basis: 36px; }
  .dashboard-action-list { grid-template-columns: 1fr; }
}
</style>
