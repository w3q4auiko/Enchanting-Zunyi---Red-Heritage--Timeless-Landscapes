/**
 * 前端应用入口模块。
 *
 * 该模块负责初始化 Vue 应用实例、装配路由与全局样式，
 * 形成旅游信息系统前端的统一启动边界。
 */

import { createApp } from "vue";

import App from "./App.vue";
import router from "./router";

import "./assets/css/main.css";
import "./assets/css/admin.css";
import "element-plus/es/components/message/style/css";
import "element-plus/es/components/message-box/style/css";

const app = createApp(App);

app.use(router);

app.mount("#app");
