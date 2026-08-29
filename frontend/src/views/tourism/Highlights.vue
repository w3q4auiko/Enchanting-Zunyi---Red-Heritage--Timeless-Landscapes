<script setup>
/**
 * @file Highlights.vue
 * @description 旅游高光页，聚合红色文化、历史遗迹与自然风光三大主题。
 * 设计意图：以专题分栏形成“重点推荐”入口，支撑首页导览与内容分发。
 * 架构视角：视图层负责主题编排与路由导流，数据来自统一景点服务接口。
 */
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { fixUrl } from "@/utils/common.js";
import { getAttractions } from "@/api/tourism";
import highlightsBannerUrl from "@/assets/images/banners/red-city-scroll-zine.webp";

const router = useRouter();

const redFootprints = ref([]);
const timeTraces = ref([]);
const danxiaScenery = ref([]);
const isLoading = ref(true);

/**
 * 将景点实体映射为通用卡片模型。
 * @param {Array<Object>} items - 后端返回的景点实体列表。
 * @returns {Array<Object>} 适配视图渲染的卡片数据。
 */
const mapData = (items) => {
  if (!Array.isArray(items)) return [];
  return items.map((item) => {
    const rawDesc = item.summary || item.description || "";
    return {
      id: item.id,
      title: item.title || "未命名景点",
      desc: rawDesc,
      type: item.entity_type || "scenery",
      img: fixUrl(item.banner_url) || fixUrl(item.image_url),
    };
  });
};

/**
 * 解析实体类型到统一详情路由。
 * @param {string} type - 实体类型标识。
 * @param {string|number} id - 实体主键。
 * @returns {string} 详情页路由路径。
 */
const resolveDetailPath = (type, id) => {
  const normalized = String(type || "scenery").toLowerCase();
  const typeToPath = {
    scenery: "scenery",
    attraction: "scenery",
    food: "food",
    region: "region",
    route: "route",
    food_street: "food-street",
    "food-street": "food-street",
  };
  return `/attraction/${typeToPath[normalized] || "scenery"}/${id}`;
};

/**
 * 并行拉取三类高光数据并完成视图模型装配。
 * @returns {Promise<void>} 完成后更新加载态。
 */
const fetchData = async () => {
  try {
    isLoading.value = true;
    const [data1, data2, data3] = await Promise.all([
      getAttractions("红色文化"),
      getAttractions("历史古迹"),
      getAttractions("自然风光"),
    ]);

    redFootprints.value = mapData(data1);
    timeTraces.value = mapData(data2);
    danxiaScenery.value = mapData(data3);
  } catch (error) {
    console.error("Failed to load highlights data:", error);
  } finally {
    isLoading.value = false;
  }
};

/**
 * 跳转至实体详情页。
 * @param {Object} item - 卡片数据。
 * @returns {Promise<void>} 路由导航结果。
 */
const goToDetail = (item) => {
  router.push(resolveDetailPath(item.type, item.id));
};

/**
 * 截取用于首页预览的短列表。
 * @param {Array<Object>} items - 完整列表。
 * @returns {Array<Object>} 预览列表。
 */
const previewList = (items) => items.slice(0, 3);

/**
 * 跳转至主题列表页。
 * @param {string} section - 主题分区标识。
 * @returns {Promise<void>} 路由导航结果。
 */
const goToList = (section) => router.push(`/highlights/list/${section}`);

onMounted(fetchData);
</script>

<template>
  <div class="page-wrapper flex flex-col min-h-screen bg-[#f6f0e6]">
    <main class="w-full flex-grow overflow-hidden">
      <section
        class="relative h-[500px] w-full overflow-hidden flex items-center justify-center"
      >
        <div
          class="absolute inset-0 bg-cover bg-center transition-transform duration-[2s] hover:scale-105"
          :style="{ backgroundImage: `url(${highlightsBannerUrl})` }"
        ></div>
        <div
          class="absolute inset-0 bg-gradient-to-b from-black/60 via-black/20 to-[#f6f0e6]"
        ></div>

        <div
          class="relative z-10 text-center text-white px-4 animate-fade-in-up"
        >
          <h1
            class="text-5xl md:text-7xl font-extrabold mb-6 tracking-widest font-serif drop-shadow-lg"
          >
            一城山水经典，千秋红色诗篇
          </h1>
          <p
            class="text-xl font-light opacity-90 max-w-1xl mx-auto leading-relaxed"
          >
            山水为形，红色为魂。镜头穿越黔北的峡谷云海，定格在赤水河的奔流与娄山关的巍峨。在这里，自然奇观与历史印记交织——每一道山水都镌刻着长征的足迹，每一寸土地都浸润着信仰的温度。跟随我们的画面，在天地造化间，遇见一个立体而动人的遵义。
          </p>
        </div>
      </section>

      <div class="v-content-shell">
        <section class="v-section">
          <div class="mb-8 flex items-end justify-between gap-3">
            <div>
              <p class="v-title-eyebrow text-[#a61f2d]">SCARLET TRAILS</p>
              <h2 class="v-title-main">红色足迹</h2>
            </div>
            <button class="v-btn v-tap-target" @click="goToList('red')">
              查看全部（{{ redFootprints.length }}）
            </button>
          </div>
          <div
            v-if="isLoading"
            class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-7"
          >
            <div
              v-for="i in 3"
              :key="`red-skeleton-${i}`"
              class="v-card v-touch-card overflow-hidden"
            >
              <div class="skeleton h-48 sm:h-56 w-full"></div>
              <div class="p-6 space-y-3">
                <div class="skeleton skeleton-line w-2/3"></div>
                <div class="skeleton skeleton-line w-full"></div>
                <div class="skeleton skeleton-line w-5/6"></div>
              </div>
            </div>
          </div>
          <div
            v-else
            class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-7"
          >
            <article
              v-for="item in previewList(redFootprints)"
              :key="`r-${item.id}`"
              class="v-card v-touch-card overflow-hidden cursor-pointer"
              @click="goToDetail(item)"
            >
              <img
                :src="item.img"
                :alt="item.title"
                class="h-48 sm:h-56 w-full object-cover"
                loading="lazy"
                decoding="async"
              />
              <div class="p-6">
                <h3 class="text-xl font-bold text-slate-900 line-clamp-1">
                  {{ item.title }}
                </h3>
                <p class="text-slate-500 text-sm mt-2 line-clamp-2">
                  {{ item.desc }}
                </p>
              </div>
            </article>
          </div>
        </section>

        <section class="v-section">
          <div class="mb-8 flex items-end justify-between gap-3">
            <button class="v-btn v-tap-target" @click="goToList('time')">
              查看全部（{{ timeTraces.length }}）
            </button>
            <div class="text-right">
              <p class="v-title-eyebrow text-[#29312e]">ECHOES OF TIME</p>
              <h2 class="v-title-main">岁月留痕</h2>
            </div>
          </div>
          <div
            v-if="isLoading"
            class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6"
          >
            <div
              v-for="i in 4"
              :key="`time-skeleton-${i}`"
              class="v-card v-touch-card overflow-hidden"
            >
              <div class="skeleton h-40 sm:h-44 w-full"></div>
              <div class="p-4 space-y-3">
                <div class="skeleton skeleton-line w-2/3"></div>
                <div class="skeleton skeleton-line w-full"></div>
                <div class="skeleton skeleton-line w-5/6"></div>
              </div>
            </div>
          </div>
          <div
            v-else
            class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6"
          >
            <article
              v-for="item in previewList(timeTraces)"
              :key="`t-${item.id}`"
              class="v-card v-touch-card overflow-hidden cursor-pointer"
              @click="goToDetail(item)"
            >
              <img
                :src="item.img"
                :alt="item.title"
                class="h-40 sm:h-44 w-full object-cover"
                loading="lazy"
                decoding="async"
              />
              <div class="p-4">
                <h3 class="text-lg font-bold text-slate-900 line-clamp-1">
                  {{ item.title }}
                </h3>
                <p class="text-slate-500 text-sm mt-2 line-clamp-2">
                  {{ item.desc }}
                </p>
              </div>
            </article>
          </div>
        </section>

        <section class="v-section">
          <div class="mb-8 flex items-end justify-between gap-3">
            <div>
              <p class="v-title-eyebrow text-[#687565]">CHARMING NATURE</p>
              <h2 class="v-title-main">醉美自然</h2>
            </div>
            <button class="v-btn v-tap-target" @click="goToList('nature')">
              查看全部（{{ danxiaScenery.length }}）
            </button>
          </div>
          <div
            v-if="isLoading"
            class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-7"
          >
            <div
              v-for="i in 3"
              :key="`nature-skeleton-${i}`"
              class="v-card v-touch-card overflow-hidden"
            >
              <div class="skeleton h-[300px] sm:h-[340px] md:h-[380px] w-full"></div>
              <div class="p-6 space-y-3">
                <div class="skeleton skeleton-line w-2/3"></div>
                <div class="skeleton skeleton-line w-full"></div>
                <div class="skeleton skeleton-line w-5/6"></div>
              </div>
            </div>
          </div>
          <div
            v-else
            class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-7"
          >
            <article
              v-for="item in previewList(danxiaScenery)"
              :key="`d-${item.id}`"
              class="group v-touch-card relative h-[300px] sm:h-[340px] md:h-[380px] rounded-3xl overflow-hidden cursor-pointer"
              @click="goToDetail(item)"
            >
              <img
                :src="item.img"
                :alt="item.title"
                class="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                loading="lazy"
                decoding="async"
              />
              <div
                class="absolute inset-0 bg-gradient-to-t from-[#687565]/80 via-black/20 to-transparent"
              ></div>
              <div class="absolute bottom-0 left-0 p-5 md:p-6 text-white">
                <h3 class="text-xl md:text-2xl font-bold line-clamp-1">
                  {{ item.title }}
                </h3>
                <p class="text-sm text-white/90 mt-2 line-clamp-2">
                  {{ item.desc }}
                </p>
              </div>
            </article>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>
