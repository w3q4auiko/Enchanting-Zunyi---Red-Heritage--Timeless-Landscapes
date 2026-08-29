<script setup>
/**
 * @file HighlightsList.vue
 * @description 高光主题列表页，承载单一主题的深度浏览。
 * 设计意图：以路由参数驱动主题切换，形成可复用的专题列表模板。
 * 架构视角：视图层统一详情路由解析，降低多实体类型跳转的耦合度。
 */
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getAttractions } from "@/api/tourism";
import { fixUrl } from "@/utils/common";

const route = useRoute();
const router = useRouter();

const sections = {
  red: { title: "红色足迹", category: "红色文化", tone: "#a61f2d" },
  time: { title: "岁月留痕", category: "历史古迹", tone: "#29312e" },
  nature: { title: "丹霞碧水", category: "自然风光", tone: "#687565" },
};

const list = ref([]);

const loading = ref(true);

/**
 * 当前主题配置，用于驱动标题与查询类别。
 * @returns {import("vue").ComputedRef<Object>} 主题配置对象。
 */
const current = computed(() => sections[route.params.section] || sections.red);

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
 * 拉取主题数据并映射为卡片视图模型。
 * @returns {Promise<void>} 数据装载完成后更新加载态。
 */
const loadData = async () => {
  try {
    loading.value = true;
    const data = await getAttractions(current.value.category);

    list.value = (Array.isArray(data) ? data : []).map((item) => ({
      id: item.id,
      title: item.title || "未命名景点",
      desc: item.summary || item.description || "",

      img: fixUrl(item.banner_url) || fixUrl(item.image_url),
      type: item.entity_type || "scenery",
    }));
  } catch (err) {
    console.error("Infrastructure: Landscape list extraction failed.", err);
  } finally {
    loading.value = false;
  }
};

/**
 * 跳转至实体详情页。
 * @param {Object} item - 卡片数据。
 * @returns {Promise<void>} 路由导航结果。
 */
const goDetail = (item) => router.push(resolveDetailPath(item.type, item.id));

onMounted(loadData);
</script>

<template>
  <main class="min-h-screen bg-[#f6f0e6]">
    <section class="v-content-shell">
      <div
        class="flex items-center justify-between mb-8 gap-4 border-b border-gray-100 pb-6"
      >
        <div>
          <p class="v-title-eyebrow" :style="{ color: current.tone }">
            HIGHLIGHTS DIRECTORY
          </p>
          <h1 class="v-title-main">{{ current.title }} · 深度发现</h1>
        </div>
        <button class="v-btn v-tap-target" @click="router.back()">返回</button>
      </div>

      <div
        v-if="loading"
        class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-7"
      >
        <div
          v-for="i in 6"
          :key="`highlights-list-skeleton-${i}`"
          class="v-card v-touch-card overflow-hidden"
        >
          <div class="skeleton h-52 w-full"></div>
          <div class="p-6 space-y-3">
            <div class="skeleton skeleton-line w-2/3"></div>
            <div class="skeleton skeleton-line w-full"></div>
            <div class="skeleton skeleton-line w-5/6"></div>
          </div>
        </div>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-7">
        <article
          v-for="item in list"
          :key="item.id"
          class="v-card v-touch-card overflow-hidden cursor-pointer group"
          @click="goDetail(item)"
        >
          <img
            :src="item.img"
            :alt="item.title"
            class="h-52 w-full object-cover group-hover:scale-105 transition-transform duration-700 ease-in-out"
            loading="lazy"
            decoding="async"
          />

          <div class="p-6">
            <h3
              class="text-xl font-bold text-slate-900 group-hover:text-blue-600 transition-colors"
            >
              {{ item.title }}
            </h3>

            <p class="text-sm text-slate-500 mt-3 line-clamp-2 leading-relaxed">
              {{ item.desc }}
            </p>
          </div>
        </article>
      </div>

      <div
        v-if="!loading && list.length === 0"
        class="text-center py-24 text-slate-400 italic"
      >
        当前分类下暂无收录数据
      </div>
    </section>
  </main>
</template>
