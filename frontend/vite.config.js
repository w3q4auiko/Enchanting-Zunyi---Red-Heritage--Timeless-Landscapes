/**
 * @file vite.config.js
 * @description 前端构建与开发服务配置，定义插件体系、代理与产物拆分策略。
 * 设计意图：通过图像压缩与手动分包优化首屏体积，并以反向代理对接后端服务。
 * 架构视角：构建阶段关注静态资源治理，运行阶段保持与 API 网关的解耦。
 */
import { ViteImageOptimizer } from "vite-plugin-image-optimizer";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import AutoImport from "unplugin-auto-import/vite";
import Components from "unplugin-vue-components/vite";
import { ElementPlusResolver } from "unplugin-vue-components/resolvers";
import path from "path";

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      dts: false,
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      dts: false,
      resolvers: [ElementPlusResolver({ importStyle: "css" })],
    }),
    ViteImageOptimizer({
      includePublic: true,
      jpeg: { quality: 75 },
      jpg: { quality: 75 },
      png: { quality: 75 },
      webp: { lossless: false, quality: 75 },
    }),
  ],
  server: {
    host: "0.0.0.0",
    port: 5173,
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    outDir: "dist",
    assetsInlineLimit: 4096,
    sourcemap: false,
    chunkSizeWarningLimit: 800,
    rollupOptions: {
      output: {
        manualChunks: {
          "vendor-core": ["vue", "vue-router"],
        },
        entryFileNames: "assets/[name]-[hash].js",
        chunkFileNames: "assets/[name]-[hash].js",
        assetFileNames: "assets/[name]-[hash].[ext]",
      },
    },
  },
});
