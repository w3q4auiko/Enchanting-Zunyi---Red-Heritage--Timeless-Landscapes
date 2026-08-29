<script setup>
/**
 * 平台关于页组件。
 *
 * 该组件用于展示遵义旅游信息系统的产品愿景、业务模块与工程化底座，
 * 形成对外介绍与品牌叙事的权威入口。
 */

import { onMounted } from "vue";

/**
 * 初始化滚动入场动画观察器。
 * @returns {void}
 */
const setupScrollReveal = () => {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 },
  );

  document
    .querySelectorAll(".animate-box")
    .forEach((el) => observer.observe(el));
};

onMounted(setupScrollReveal);
</script>

<template>
  <div
    class="page-wrapper flex flex-col min-h-screen bg-slate-50 font-sans selection:bg-rose-200 selection:text-rose-900"
  >
    <main class="w-full flex-grow relative overflow-hidden pb-20">
      <div
        class="absolute top-0 left-0 w-full h-[500px] bg-gradient-to-b from-rose-100/50 to-slate-50 pointer-events-none -z-10"
      ></div>
      <div
        class="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-rose-200/30 rounded-full blur-[100px] pointer-events-none -z-10"
      ></div>
      <div
        class="absolute top-[20%] left-[-10%] w-[400px] h-[400px] bg-emerald-100/40 rounded-full blur-[80px] pointer-events-none -z-10"
      ></div>

      <div class="max-w-[1200px] mx-auto px-6 py-16 md:py-24 space-y-24">
        <section class="animate-box text-center max-w-4xl mx-auto space-y-8">
          <div
            class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white border border-slate-200 text-rose-600 text-xs font-bold tracking-widest uppercase shadow-sm"
          >
            <span class="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span>
            Enchanting Zunyi Digital Tourism Platform
          </div>
          <h1
            class="text-4xl md:text-5xl lg:text-6xl font-black text-slate-900 tracking-tight leading-tight"
            style="
              font-family:
                &quot;Songti SC&quot;, &quot;Noto Serif SC&quot;, serif;
            "
          >
            醉美遵义 ·
            <span
              class="text-transparent bg-clip-text bg-gradient-to-r from-rose-600 to-red-500"
              >山河红韵</span
            >
          </h1>
          <p class="text-slate-600 leading-relaxed text-base md:text-lg">
            本项目基于现代化的
            <span class="font-bold text-slate-800">Flask + Vue 3</span>
            技术栈倾力打造。我们不仅构建了一个全域旅游信息的数字展厅，更是将遵义的红色基因、丹霞生态与市井烟火，通过丝滑的交互体验呈现给每一位探索者。在这里，数字技术与城市文脉完美交融。
          </p>
        </section>

        <section class="animate-box">
          <div class="text-center mb-14">
            <h2 class="text-3xl font-bold text-slate-900 mb-4">
              核心模块与数字体验
            </h2>
            <p class="text-slate-500">
              从历史印记到人间烟火，为您提供一站式的沉浸向导。
            </p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <article
              class="group bg-white rounded-[2rem] p-8 shadow-sm hover:shadow-2xl hover:-translate-y-2 transition-all duration-500 border border-slate-100 relative overflow-hidden flex flex-col h-full"
            >
              <div
                class="absolute -right-8 -top-8 w-32 h-32 bg-rose-50 rounded-full group-hover:scale-150 transition-transform duration-700 ease-out -z-10"
              ></div>
              <div
                class="w-14 h-14 bg-rose-100 rounded-2xl flex items-center justify-center mb-8 text-rose-600 shadow-inner group-hover:rotate-6 transition-transform"
              >
                <svg
                  class="w-7 h-7"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                  ></path>
                </svg>
              </div>
              <h3
                class="text-xl font-bold text-slate-900 mb-4 group-hover:text-rose-600 transition-colors"
              >
                红城印象 & 画卷
              </h3>
              <p class="text-slate-500 text-[15px] leading-relaxed flex-grow">
                以长征史诗为线索，串联遵义会议会址、娄山关等核心地标。景观聚合中心涵盖红色足迹、历史古迹与醉美自然（丹霞地貌），展现转折之地的城市底蕴。
              </p>
            </article>

            <article
              class="group bg-white rounded-[2rem] p-8 shadow-sm hover:shadow-2xl hover:-translate-y-2 transition-all duration-500 border border-slate-100 relative overflow-hidden flex flex-col h-full"
            >
              <div
                class="absolute -right-8 -top-8 w-32 h-32 bg-amber-50 rounded-full group-hover:scale-150 transition-transform duration-700 ease-out -z-10"
              ></div>
              <div
                class="w-14 h-14 bg-amber-100 rounded-2xl flex items-center justify-center mb-8 text-amber-600 shadow-inner group-hover:rotate-6 transition-transform"
              >
                <svg
                  class="w-7 h-7"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                  ></path>
                </svg>
              </div>
              <h3
                class="text-xl font-bold text-slate-900 mb-4 group-hover:text-amber-600 transition-colors"
              >
                黔北食韵 & 探幽
              </h3>
              <p class="text-slate-500 text-[15px] leading-relaxed flex-grow">
                细分粉面文化、风味市井与地道佳肴，提供人均消费与店铺导引。同时提供山野徒步路线（含难度系数/耗时/里程）与市井烟火街区索引的深度旅游指南。
              </p>
            </article>

            <article
              class="group bg-white rounded-[2rem] p-8 shadow-sm hover:shadow-2xl hover:-translate-y-2 transition-all duration-500 border border-slate-100 relative overflow-hidden flex flex-col h-full"
            >
              <div
                class="absolute -right-8 -top-8 w-32 h-32 bg-blue-50 rounded-full group-hover:scale-150 transition-transform duration-700 ease-out -z-10"
              ></div>
              <div
                class="w-14 h-14 bg-blue-100 rounded-2xl flex items-center justify-center mb-8 text-blue-600 shadow-inner group-hover:rotate-6 transition-transform"
              >
                <svg
                  class="w-7 h-7"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
                  ></path>
                </svg>
              </div>
              <h3
                class="text-xl font-bold text-slate-900 mb-4 group-hover:text-blue-600 transition-colors"
              >
                全域攻略 & 智慧交互
              </h3>
              <p class="text-slate-500 text-[15px] leading-relaxed flex-grow">
                全景展示“三区两市九县”的地理分布与交通接驳枢纽。集成高德地图接口实现
                LBS 导航分发，支持多态搜索过滤，并开放 UGC
                用户内容贡献在线提交。
              </p>
            </article>
          </div>
        </section>

        <section class="animate-box">
          <div
            class="bg-slate-900 rounded-[2.5rem] p-10 md:p-16 text-slate-100 shadow-2xl relative overflow-hidden"
          >
            <div
              class="absolute top-0 right-0 w-[600px] h-[600px] bg-gradient-to-br from-indigo-500/20 to-transparent rounded-full blur-[100px] -translate-y-1/2 translate-x-1/3"
            ></div>

            <h2 class="text-3xl font-bold mb-14 text-white relative z-10">
              驱动体验的工程化底座
            </h2>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 relative z-10">
              <div class="space-y-6">
                <div class="flex items-start gap-5">
                  <div
                    class="mt-1 w-12 h-12 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0"
                  >
                    <span class="text-emerald-400 font-bold text-xl"
                      >&lt;/&gt;</span
                    >
                  </div>
                  <div>
                    <h3 class="text-xl font-bold text-white mb-2">
                      全栈敏捷架构落地
                    </h3>
                    <p class="text-slate-400 text-sm leading-relaxed">
                      前台依托
                      <span class="text-emerald-400 font-medium"
                        >Vue 3 + Vite</span
                      >
                      构建无感知路由体系，配合 Tailwind CSS 与 Element Plus
                      实现全端响应式适配。后台采用
                      <span class="text-rose-400 font-medium"
                        >Python Flask 3</span
                      >
                      驱动，铺设结构化的 RESTful 接口管线，保障极致的响应速度。
                    </p>
                  </div>
                </div>
              </div>

              <div class="space-y-6">
                <div class="flex items-start gap-5">
                  <div
                    class="mt-1 w-12 h-12 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0"
                  >
                    <svg
                      class="w-6 h-6 text-blue-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                      ></path>
                    </svg>
                  </div>
                  <div>
                    <h3 class="text-xl font-bold text-white mb-2">
                      闭环的内容生态与鉴权
                    </h3>
                    <p class="text-slate-400 text-sm leading-relaxed">
                      内建完整的后台管理域（Dashboard），覆盖景点、美食、线路的全量
                      CRUD 生命周期管理。支持 UGC 投稿审核流水线，底层引入
                      <span class="text-blue-400 font-medium"
                        >JWT Token 身份令牌</span
                      >校验，阻断越权访问风险。
                    </p>
                  </div>
                </div>
              </div>

              <div class="space-y-6">
                <div class="flex items-start gap-5">
                  <div
                    class="mt-1 w-12 h-12 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0"
                  >
                    <svg
                      class="w-6 h-6 text-amber-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"
                      ></path>
                    </svg>
                  </div>
                  <div>
                    <h3 class="text-xl font-bold text-white mb-2">
                      高并发数据缓冲池
                    </h3>
                    <p class="text-slate-400 text-sm leading-relaxed">
                      基于 MySQL 8.0 核心存储，底层深度集成
                      <span class="text-amber-400 font-medium"
                        >DBUtils 数据库连接池技术</span
                      >与
                      PyMySQL，有效复用数据库连接，大幅降低高频并发访问下的系统开销。
                    </p>
                  </div>
                </div>
              </div>

              <div class="space-y-6">
                <div class="flex items-start gap-5">
                  <div
                    class="mt-1 w-12 h-12 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0"
                  >
                    <svg
                      class="w-6 h-6 text-cyan-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                      ></path>
                    </svg>
                  </div>
                  <div>
                    <h3 class="text-xl font-bold text-white mb-2">
                      云原生容器化基建
                    </h3>
                    <p class="text-slate-400 text-sm leading-relaxed">
                      面向现代生产环境，全面提供
                      <span class="text-cyan-400 font-medium"
                        >Docker Compose</span
                      >
                      容器编排支持。外网流量经由 Nginx
                      高效反向代理与静态资源托管，内网交由 Gunicorn WSGI
                      进程池进行高可用吞吐调度。
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<style scoped>
/*
 * 视口入场动效样式。
 * 通过 Intersection Observer 触发类名，形成分区滚动揭示效果。
 */
.animate-box {
  opacity: 0;
  transform: translateY(40px) translateZ(0);
  transition:
    opacity 0.8s cubic-bezier(0.25, 1, 0.3, 1),
    transform 0.8s cubic-bezier(0.25, 1, 0.3, 1);
  will-change: transform, opacity;
}

.animate-box.is-visible {
  opacity: 1;
  transform: translateY(0) translateZ(0);
}
</style>
