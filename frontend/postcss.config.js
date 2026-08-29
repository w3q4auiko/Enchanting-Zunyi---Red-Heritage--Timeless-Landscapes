/**
 * @file postcss.config.js
 * @description PostCSS 管线配置，集成 Tailwind 与 Autoprefixer。
 * 设计意图：保证样式编译与跨浏览器兼容性，支撑旅游信息系统的多终端展示。
 */
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
