<script setup>
/**
 * @file Taste.vue
 * @description 美食文化聚合页，面向旅游信息系统的“城市风味入口”场景。
 * 设计意图：以分区卡片聚合多品类美食与街区数据，形成可导览的内容索引。
 * 架构视角：采用组合式 API 作为视图编排层，结合基于路由的模块化导航与
 * 并行数据装载策略，降低首屏等待与渲染耦合。
 */
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { fixUrl } from "@/utils/common.js";
import { getFoods, getFoodStreets } from "@/api/tourism";
import tasteBannerUrl from "@/assets/images/banners/qianbei-taste-zine.webp";

const router = useRouter();


const isLoading = ref(true);

const foodStreets = ref([]);


const sections = [
  {
    id: "noodle",
    title: "粉面文化",
    subtitle: "NOODLE CULTURE",
    category: "遵义粉面",
    tone: "#687565",
  },
  {
    id: "snack",
    title: "风味市井",
    subtitle: "STREET SNACKS",
    category: "街头小吃",
    tone: "#a61f2d",
  },
  {
    id: "feast",
    title: "黔北佳肴",
    subtitle: "LOCAL DISHES",
    category: "地道大菜",
    tone: "#b77b3b",
  },
  {
    id: "dessert",
    title: "清凉甜饮",
    subtitle: "COLD TREATS",
    category: "甜品冷饮",
    tone: "#a74a55",
  },
  {
    id: "tea",
    title: "茶酒飘香",
    subtitle: "BREWS & BLENDS",
    category: "名茶佳酿",
    tone: "#586b55",
  },
  {
    id: "mountain",
    title: "深山寻珍",
    subtitle: "NATURE FLAVORS",
    category: "山珍寻味",
    tone: "#586a54",
  },
  {
    id: "gift",
    title: "风物好礼",
    subtitle: "SOUVENIRS",
    category: "特产手信",
    tone: "#84505a",
  },
];


const buckets = reactive({});


/**
 * 将美食实体映射为通用卡片模型。
 * @param {Array<Object>} items - 后端返回的美食实体列表。
 * @returns {Array<Object>} 适配视图渲染的卡片数据。
 */
const mapData = (items) => {
  if (!Array.isArray(items)) return [];
  return items.map((item) => ({
    id: item.id,
    title: item.name || "未命名美食",
    desc: item.description || item.tips || "",
    price: item.price || "",
    img: fixUrl(item.image_url) || fixUrl(item.banner_url),
    url: `/attraction/food/${item.id}`,
  }));
};


/**
 * 将美食街区实体映射为通用卡片模型。
 * @param {Array<Object>} items - 后端返回的街区实体列表。
 * @returns {Array<Object>} 适配视图渲染的卡片数据。
 */
const mapStreetData = (items) => {
  if (!Array.isArray(items)) return [];
  return items.map((item) => ({
    id: item.id,
    title: item.name || "未命名街区",
    desc: item.description || item.alias || "",
    img:
      fixUrl(item.banner_url) ||
      fixUrl(item.image_url) ||
      "/img/banner_3.jpg",
    url: `/attraction/food-street/${item.id}`,
  }));
};

/**
 * 并行拉取分区美食与街区数据，构建分栏展示的视图模型。
 * @returns {Promise<void>} 完成后同步刷新页面状态。
 */
const fetchData = async () => {
  try {
    isLoading.value = true;
    const [foodResponses, streets] = await Promise.all([
      Promise.all(sections.map((s) => getFoods(s.category))),
      getFoodStreets(),
    ]);
    sections.forEach((section, idx) => {
      buckets[section.id] = mapData(foodResponses[idx]);
    });
    foodStreets.value = mapStreetData(streets);
  } catch (err) {
    console.error("Infrastructure: Culinary data fetch failed.", err);
    
    sections.forEach((section) => {
      buckets[section.id] = [];
    });
    foodStreets.value = [];
  } finally {
    isLoading.value = false;
  }
};



onMounted(fetchData);


/**
 * 截取用于首屏预览的短列表。
 * @param {Array<Object>} items - 完整数据集。
 * @returns {Array<Object>} 预览数据集。
 */
const previewList = (items) => (Array.isArray(items) ? items.slice(0, 3) : []);


/**
 * 计算分区内可展示的数据总量。
 * @param {string} sectionId - 分区标识。
 * @returns {number} 数据总量。
 */
const totalCount = (sectionId) =>
  Array.isArray(buckets[sectionId]) ? buckets[sectionId].length : 0;


/**
 * 跳转至对应分区的列表视图。
 * @param {string} sectionId - 分区标识。
 * @returns {Promise<void>} 路由导航结果。
 */
const goToList = (sectionId) => router.push(`/taste/list/${sectionId}`);


/**
 * 组装分区卡片的视图模型集合。
 * @returns {import("vue").ComputedRef<Array<Object>>} 分区卡片集合。
 */
const sectionCards = computed(() =>
  sections.map((section) => ({
    ...section,
    preview: previewList(buckets[section.id]),
    total: totalCount(section.id),
  })),
);
</script>

<template>
  <div class="page-wrapper flex flex-col min-h-screen bg-[#f6f0e6]">
    <main class="w-full flex-grow overflow-hidden">
      
      <section
        class="relative h-[500px] w-full overflow-hidden flex items-center justify-center"
      >
        <div
          class="absolute inset-0 bg-cover bg-center transition-transform duration-[2s] hover:scale-105"
          :style="{ backgroundImage: `url(${tasteBannerUrl})` }"
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
            舌尖上的黔北，烟火里的遵义
          </h1>
          <p
            class="text-xl font-light opacity-90 max-w-1xl mx-auto leading-relaxed"
          >
            在遵义的街巷深处，每一道小吃都藏着山地气候的脾气，每一碗热汤都煨着老城生活的温度。从清晨的豆花面到深夜的烧烤摊，在一餐一味之间，尝遍黔北风土。
          </p>
        </div>
      </section>

      <div class="v-content-shell">
        
        <section
          v-for="section in sectionCards"
          :key="section.id"
          class="v-section"
        >
          
          <div class="mb-8 flex items-end justify-between gap-3">
            <div>
              <p class="v-title-eyebrow" :style="{ color: section.tone }">
                {{ section.subtitle }}
              </p>
              <h2 class="v-title-main">{{ section.title }}</h2>
            </div>
            <button class="v-btn v-tap-target" @click="goToList(section.id)">
              查看全部（{{ section.total }}）
            </button>
          </div>

          
          <div
            v-if="isLoading"
            class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6"
          >
            <div
              v-for="i in 3"
              :key="`${section.id}-skeleton-${i}`"
              class="v-card v-touch-card overflow-hidden"
            >
              <div class="skeleton h-44 w-full"></div>
              <div class="p-4 space-y-3">
                <div class="skeleton skeleton-line w-2/3"></div>
                <div class="skeleton skeleton-line w-full"></div>
                <div class="skeleton skeleton-line w-5/6"></div>
              </div>
            </div>
          </div>

          <div
            v-else
            class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6"
          >
            <article
              v-for="item in section.preview"
              :key="`${section.id}-${item.id}`"
              class="v-card v-touch-card overflow-hidden cursor-pointer group"
              @click="router.push(item.url)"
            >
              
              <img
                :src="item.img"
                :alt="item.title"
                class="h-44 w-full object-cover group-hover:scale-105 transition-transform duration-500"
                loading="lazy"
                decoding="async"
              />
              <div class="p-4">
                <div class="flex justify-between items-start gap-2">
                  <h3 class="font-bold text-slate-900 line-clamp-1">
                    {{ item.title }}
                  </h3>
                  
                  <span
                    v-if="item.price"
                    class="text-xs text-rose-600 font-semibold"
                    >¥{{ item.price }}</span
                  >
                </div>
                <p
                  class="text-xs text-slate-500 mt-2 line-clamp-2 leading-relaxed"
                >
                  {{ item.desc }}
                </p>
              </div>
            </article>
          </div>
        </section>

        
        <section class="v-section">
          <div class="mb-8 flex items-end justify-between gap-3">
            <button class="v-btn v-tap-target" @click="goToList('streets')">
              查看全部（{{ foodStreets.length }}）
            </button>
            <div class="text-right">
              <p class="v-title-eyebrow text-[#7a4b24]">FOOD STREETS</p>
              <h2 class="v-title-main">市井烟火</h2>
            </div>
          </div>

          <div
            v-if="isLoading"
            class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-7"
          >
            <div
              v-for="i in 3"
              :key="`street-skeleton-${i}`"
              class="v-card v-touch-card overflow-hidden"
            >
              <div class="skeleton h-44 sm:h-52 w-full"></div>
              <div class="p-5 space-y-3">
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
              v-for="item in previewList(foodStreets)"
              :key="`f-${item.id}`"
              class="v-card v-touch-card overflow-hidden cursor-pointer"
              @click="router.push(item.url)"
            >
              <img
                :src="item.img"
                :alt="item.title"
                class="h-44 sm:h-52 w-full object-cover"
                loading="lazy"
                decoding="async"
              />
              <div class="p-5">
                <h3 class="text-xl font-bold text-slate-900 line-clamp-1">
                  {{ item.title }}
                </h3>
                <p class="text-sm text-slate-500 mt-2 line-clamp-2">
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

