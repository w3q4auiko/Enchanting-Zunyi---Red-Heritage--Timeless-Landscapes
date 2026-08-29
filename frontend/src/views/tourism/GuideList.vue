<script setup>
/**
 * @file GuideList.vue
 * @description 区域分类列表页，承载“行政区划”分层后的深入浏览。
 * 设计意图：以配置驱动筛选策略，复用统一的区域列表渲染管线。
 * 架构视角：视图层只负责过滤编排与导航输出，数据来源保持后端统一。
 */
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getRegions } from "@/api/tourism";
import { fixUrl } from "@/utils/common";

const route = useRoute();
const router = useRouter();




const sections = {
  districts: {
    title: "中心城区",
    filterFn: (item) => item.type === "市辖区",
    tone: "#586b55",
  },
  cities: {
    title: "特色县级市",
    filterFn: (item) => item.type === "县级市",
    tone: "#687565",
  },
  counties: {
    title: "县域目的地",
    filterFn: (item) => ["县", "自治县"].includes(item.type),
    tone: "#b58a4b",
  },
};




const list = ref([]);

const loading = ref(true);


/**
 * 当前分区配置，驱动标题与筛选规则。
 * @returns {import("vue").ComputedRef<Object>} 分区配置对象。
 */
const current = computed(
  () => sections[route.params.section] || sections.districts,
);




/**
 * 拉取区域数据并按当前分区规则进行过滤与映射。
 * @returns {Promise<void>} 数据装载完成后更新列表状态。
 */
const loadData = async () => {
  try {
    loading.value = true;
    const data = await getRegions();

    
    const filteredData = (Array.isArray(data) ? data : []).filter(
      current.value.filterFn,
    );

    
    list.value = filteredData.map((item) => ({
      id: item.id,
      title: item.name || "未命名区域",
      desc: item.description || item.summary || "",
      img:
        fixUrl(item.banner_url) ||
        fixUrl(item.image_url) ||
        "/img/scenery/placeholder_region.jpg",
    }));
  } catch (err) {
    console.error("Infrastructure: Region list extraction failed.", err);
  } finally {
    loading.value = false;
  }
};


/**
 * 跳转到区域详情页。
 * @param {Object} item - 列表卡片数据。
 * @returns {Promise<void>} 路由导航结果。
 */
const goDetail = (item) => {
  router.push(`/attraction/region/${item.id}?type=region`);
};


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
            REGIONAL DIRECTORY
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
          :key="`guide-list-skeleton-${i}`"
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

