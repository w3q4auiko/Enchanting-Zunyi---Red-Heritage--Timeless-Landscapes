<script setup>
/**
 * @file TasteList.vue
 * @description 美食分区列表页，用于承载“舌尖文化”分类的深度浏览。
 * 设计意图：通过路由参数驱动分区切换，复用统一的列表渲染管线。
 * 架构视角：视图层仅负责数据编排与路由导航，实体筛选交由配置驱动。
 */
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getFoods, getFoodStreets } from "@/api/tourism";
import { fixUrl } from "@/utils/common";

const route = useRoute();
const router = useRouter();

const sections = {
  noodle: { title: "遵义粉面", category: "遵义粉面", tone: "#687565" },
  snack: { title: "街头小吃", category: "街头小吃", tone: "#a61f2d" },
  feast: { title: "地道大菜", category: "地道大菜", tone: "#b77b3b" },
  dessert: { title: "甜品冷饮", category: "甜品冷饮", tone: "#a74a55" },
  tea: { title: "名茶佳酿", category: "名茶佳酿", tone: "#586b55" },
  mountain: { title: "山珍寻味", category: "山珍寻味", tone: "#586a54" },
  gift: { title: "特产手信", category: "特产手信", tone: "#84505a" },
  streets: { title: "美食街区", tone: "#7a4b24" },
};

const list = ref([]);

const loading = ref(true);

/**
 * 当前分区的视图描述，用于驱动列表标题与数据过滤。
 * @returns {import("vue").ComputedRef<Object>} 当前分区配置。
 */
const current = computed(
  () => sections[route.params.section] || sections.noodle,
);

/**
 * 按分区拉取后端数据并构建统一的展示模型。
 * @returns {Promise<void>} 数据加载完成后同步更新列表状态。
 */
const loadData = async () => {
  try {
    loading.value = true;
    if (route.params.section === "streets") {
      const data = await getFoodStreets();
      list.value = (Array.isArray(data) ? data : []).map((item) => ({
        id: item.id,
        title: item.name || "未命名街区",
        desc: item.description || item.alias || "",
        img:
          fixUrl(item.banner_url) ||
          fixUrl(item.image_url) ||
          "/img/banner_3.jpg",
        type: "food-street",
      }));
      return;
    }

    const data = await getFoods(current.value.category);

    list.value = (Array.isArray(data) ? data : []).map((item) => ({
      id: item.id,
      title: item.name || "未命名美食",
      desc: item.description || item.tips || "",
      price: item.price,

      img: fixUrl(item.banner_url) || fixUrl(item.image_url),
      type: "food",
    }));
  } catch (err) {
    console.error("Infrastructure: Culinary list extraction failed.", err);
  } finally {
    loading.value = false;
  }
};

/**
 * 根据实体类型跳转至对应详情页。
 * @param {Object} item - 视图卡片数据。
 * @returns {Promise<void>} 路由导航结果。
 */
const goDetail = (item) => {
  if (item.type === "food-street") {
    router.push(`/attraction/food-street/${item.id}`);
    return;
  }
  router.push(`/attraction/food/${item.id}`);
};

watch(() => route.params.section, loadData, { immediate: true });
</script>

<template>
  <main class="min-h-screen bg-[#f6f0e6]">
    <section class="v-content-shell">
      <div
        class="flex items-center justify-between mb-6 gap-4 border-b border-gray-100 pb-6"
      >
        <div>
          <p class="v-title-eyebrow" :style="{ color: current.tone }">
            TASTE EXPLORATION
          </p>
          <h1 class="v-title-main">{{ current.title }} · 分类列表</h1>
        </div>
        <button class="v-btn v-tap-target" @click="router.back()">返回</button>
      </div>

      <div
        v-if="loading"
        class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6"
      >
        <div
          v-for="i in 6"
          :key="`taste-list-skeleton-${i}`"
          class="v-card v-touch-card overflow-hidden"
        >
          <div class="skeleton h-52 w-full"></div>
          <div class="p-5 space-y-3">
            <div class="skeleton skeleton-line w-2/3"></div>
            <div class="skeleton skeleton-line w-full"></div>
            <div class="skeleton skeleton-line w-5/6"></div>
          </div>
        </div>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        <article
          v-for="item in list"
          :key="item.id"
          class="v-card v-touch-card overflow-hidden cursor-pointer group"
          @click="goDetail(item)"
        >
          <img
            :src="item.img"
            :alt="item.title"
            class="h-52 w-full object-cover group-hover:scale-105 transition-transform duration-500"
            loading="lazy"
            decoding="async"
          />

          <div class="p-5">
            <div class="flex items-start justify-between gap-2">
              <h3 class="text-lg font-bold text-slate-900 line-clamp-1">
                {{ item.title }}
              </h3>

              <span
                v-if="item.price"
                class="text-xs text-rose-600 font-semibold whitespace-nowrap"
              >
                ¥{{ item.price }}
              </span>
            </div>

            <p class="text-sm text-slate-500 mt-2 line-clamp-2 leading-relaxed">
              {{ item.desc }}
            </p>
          </div>
        </article>
      </div>

      <div
        v-if="!loading && list.length === 0"
        class="text-center py-20 text-slate-400 italic"
      >
        当前类目下暂无收录数据
      </div>
    </section>
  </main>
</template>
