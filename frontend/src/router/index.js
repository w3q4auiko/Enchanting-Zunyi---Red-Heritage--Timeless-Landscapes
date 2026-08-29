/** 应用路由表与访问控制。 */

import { ElMessage } from "element-plus";
import { createRouter, createWebHistory } from "vue-router";

import AdminLayout from "@/views/admin/AdminLayout.vue";
import { ensureSession } from "@/api/auth";
import { getUserInfo } from "@/utils/session";

// Vite 在构建期收集页面模块，路由仍保持按需加载。
const viewModules = import.meta.glob([
  "../views/**/*.vue",
  "!../views/admin/AdminLayout.vue",
]);
const view = (path) => viewModules[`../views/${path}.vue`];

const routes = [
  { path: "/", name: "Home", component: view("Home") },
  {
    path: "/login",
    name: "Login",
    component: view("Login"),
    meta: { hideLayout: true },
  },
  {
    path: "/register",
    name: "Register",
    component: view("Register"),
    meta: { hideLayout: true },
  },
  { path: "/overview", name: "Overview", component: view("tourism/Overview") },
  {
    path: "/highlights",
    name: "Highlights",
    component: view("tourism/Highlights"),
  },
  {
    path: "/highlights/list/:section",
    name: "HighlightsList",
    component: view("tourism/HighlightsList"),
  },
  { path: "/guide", name: "Guide", component: view("tourism/Guide") },
  {
    path: "/guide/list/:section",
    name: "GuideList",
    component: view("tourism/GuideList"),
  },
  { path: "/taste", name: "Taste", component: view("culture/Taste") },
  {
    path: "/taste/list/:section",
    name: "TasteList",
    component: view("culture/TasteList"),
  },
  { path: "/about", name: "About", component: view("About") },
  {
    path: "/attraction/food/:id",
    name: "FoodDetail",
    component: view("content/FoodDetail"),
  },
  {
    path: "/attraction/region/:id",
    name: "RegionDetail",
    component: view("content/RegionDetail"),
  },
  {
    path: "/attraction/scenery/:id",
    name: "AttractionDetail",
    component: view("content/Attraction"),
  },
  {
    path: "/attraction/route/:id",
    name: "RouteDetail",
    component: view("content/RouteDetail"),
  },
  {
    path: "/attraction/food-street/:id",
    name: "FoodStreetDetail",
    component: view("content/FoodStreetDetail"),
  },
  {
    path: "/user/contribute",
    name: "Contribute",
    component: view("user/Contribute"),
    meta: { requiresAuth: true },
  },
  {
    path: "/admin",
    component: AdminLayout,
    redirect: "/admin/dashboard",
    meta: { hideLayout: true, requiresAuth: true, requiresAdmin: true },
    children: [
      { path: "dashboard", name: "AdminDashboard", component: view("admin/Dashboard") },
      { path: "attraction", component: view("admin/AttractionList") },
      { path: "attraction/add", component: view("admin/AttractionForm") },
      { path: "attraction/edit/:id", component: view("admin/AttractionForm") },
      { path: "food", component: view("admin/FoodList") },
      { path: "food/add", component: view("admin/FoodForm") },
      { path: "food/edit/:id", component: view("admin/FoodForm") },
      { path: "food-street", component: view("admin/FoodStreetList") },
      { path: "food-street/add", component: view("admin/FoodStreetForm") },
      { path: "food-street/edit/:id", component: view("admin/FoodStreetForm") },
      { path: "route", component: view("admin/RouteList") },
      { path: "route/add", component: view("admin/RouteForm") },
      { path: "route/edit/:id", component: view("admin/RouteForm") },
      { path: "region", component: view("admin/RegionList") },
      { path: "region/add", component: view("admin/RegionForm") },
      { path: "region/edit/:id", component: view("admin/RegionForm") },
      { path: "user", component: view("admin/UserList") },
    ],
  },
  { path: "/:pathMatch(.*)*", redirect: "/" },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: (_to, _from, savedPosition) => savedPosition || { top: 0 },
});

router.beforeEach(async (to) => {
  const requiresSession = to.matched.some((record) => record.meta.requiresAuth);
  const authenticated = requiresSession ? await ensureSession() : false;
  const user = getUserInfo();

  if (requiresSession && !authenticated) {
    return { path: "/login", query: { redirect: to.fullPath } };
  }

  if (to.meta.requiresAdmin && user?.accountType !== "admin") {
    ElMessage.error("访问被拒绝：当前账号不具备管理员权限");
    return "/";
  }

  return true;
});

export default router;
