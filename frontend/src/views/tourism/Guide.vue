<script setup>
/**
 * @file Guide.vue
 * @description 旅游指南总览页，面向游客提供行政区划与交通引导的综合入口。
 * 设计意图：以“区域概览 + 交通指南”的双通道结构，建立到详情列表的导流路径。
 * 架构视角：视图层负责聚合区域元数据并进行分区统计，导航行为统一走路由模块。
 */
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { fixUrl } from "@/utils/common.js";
import { getRegions } from "@/api/tourism";
import guideBannerUrl from "@/assets/images/banners/qianbei-guide-zine.webp";

const router = useRouter();




const regions = ref([]);

const isLoading = ref(true);


const trafficGuides = ref([
  {
    id: "t1",
    title: "遵义新舟机场、遵义茅台机场",
    desc: "覆盖国内核心航线，配套机场快线与预约制通勤服务直达主城商务区。",
    badge: "AIRPORT",
  },
  {
    id: "t2",
    title: "高铁路网中心（遵义站等）",
    desc: "渝贵铁路枢纽节点，实现与贵阳、重庆、成都等西南核心城市的高效时空压缩。",
    badge: "RAILWAY",
  },
  {
    id: "t3",
    title: "市内公共交通与接驳体系",
    desc: "覆盖核心历史景区的公交干线，配合共享微出行与网约车实现末端接驳。",
    badge: "TRANSFER",
  },
]);




/**
 * 区域分层视图：中心城区集合。
 * @returns {import("vue").ComputedRef<Array<Object>>} 市辖区列表。
 */
const districts = computed(() =>
  regions.value.filter((item) => item.type === "市辖区"),
);

/**
 * 区域分层视图：特色县级市集合。
 * @returns {import("vue").ComputedRef<Array<Object>>} 县级市列表。
 */
const cities = computed(() =>
  regions.value.filter((item) => item.type === "县级市"),
);

/**
 * 区域分层视图：县域目的地集合。
 * @returns {import("vue").ComputedRef<Array<Object>>} 县与自治县列表。
 */
const counties = computed(() =>
  regions.value.filter((item) => ["县", "自治县"].includes(item.type)),
);




/**
 * 拉取区域元数据并规范化为视图卡片模型。
 * @returns {Promise<void>} 数据装载完成后刷新视图状态。
 */
const fetchData = async () => {
  try {
    isLoading.value = true;
    const dataRegions = await getRegions();
    if (Array.isArray(dataRegions)) {
      regions.value = dataRegions.map((item) => ({
        ...item,
        title: item.name,
        
        img: fixUrl(item.banner_url) || "/img/scenery/placeholder_region.jpg",
      }));
    }
  } catch (error) {
    console.error("Infrastructure: Regional metadata sync failed.", error);
  } finally {
    isLoading.value = false;
  }
};




/**
 * 跳转至区域详情页。
 * @param {Object} item - 区域卡片数据。
 * @returns {Promise<void>} 路由导航结果。
 */
const goToDetail = (item) => {
  router.push(`/attraction/region/${item.id}?type=region`);
};

/**
 * 截取用于首页预览的短列表。
 * @param {Array<Object>} items - 完整列表。
 * @returns {Array<Object>} 预览列表。
 */
const previewList = (items) => items.slice(0, 3);

/**
 * 跳转至分区列表页。
 * @param {string} section - 分区标识。
 * @returns {Promise<void>} 路由导航结果。
 */
const goToList = (section) => router.push(`/guide/list/${section}`);


onMounted(() => {
  fetchData();
});
</script>

<template>
  <div class="page-wrapper flex flex-col min-h-screen bg-[#f2ebe1]">
    <main class="w-full flex-grow">
      
      <section
        class="relative h-[500px] w-full overflow-hidden flex items-center justify-center"
      >
        <div
          class="absolute inset-0 bg-cover bg-center transition-transform duration-[2s] hover:scale-105"
          :style="{ backgroundImage: `url(${guideBannerUrl})` }"
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
            一册在手，走遍黔北
          </h1>
          <p
            class="text-xl font-light opacity-90 max-w-1xl mx-auto leading-relaxed"
          >
            从红城腹地到县域山水，从经典路线到小众玩法。无论是初访还是重游，都能在此张全域版图中快速定位您的遵义坐标。
          </p>
        </div>
      </section>

      
      <div class="v-content-shell">
        
        <section id="regions" class="v-section scroll-mt-44 md:scroll-mt-28">
          <div v-if="isLoading" class="space-y-12">
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-10">
              <div class="v-card-flat p-5">
                <div class="skeleton skeleton-line w-20"></div>
                <div class="skeleton h-10 w-24 mt-4"></div>
              </div>
              <div class="v-card-flat p-5">
                <div class="skeleton skeleton-line w-20"></div>
                <div class="skeleton h-10 w-24 mt-4"></div>
              </div>
              <div class="v-card-flat p-5">
                <div class="skeleton skeleton-line w-20"></div>
                <div class="skeleton h-10 w-24 mt-4"></div>
              </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div
                v-for="i in 3"
                :key="`guide-district-skeleton-${i}`"
                class="v-card v-touch-card overflow-hidden"
              >
                <div class="skeleton h-44 w-full"></div>
                <div class="p-5 space-y-3">
                  <div class="skeleton skeleton-line w-2/3"></div>
                  <div class="skeleton skeleton-line w-full"></div>
                  <div class="skeleton skeleton-line w-5/6"></div>
                </div>
              </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div
                v-for="i in 2"
                :key="`guide-city-skeleton-${i}`"
                class="relative v-touch-card h-56 rounded-2xl overflow-hidden"
              >
                <div class="skeleton h-full w-full"></div>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
              <div
                v-for="i in 3"
                :key="`guide-county-skeleton-${i}`"
                class="v-card-flat v-touch-card p-4 flex gap-4 items-center"
              >
                <div class="skeleton h-20 w-20 rounded-lg"></div>
                <div class="min-w-0 flex-1 space-y-3">
                  <div class="skeleton skeleton-line w-2/3"></div>
                  <div class="skeleton skeleton-line w-full"></div>
                </div>
              </div>
            </div>
          </div>

          <template v-else>
            
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-10">
              <div class="v-card-flat p-5 border-l-4 border-blue-600">
                <p class="text-xs text-slate-500 uppercase tracking-tighter">
                  市辖区
                </p>
                <p class="text-3xl font-black text-slate-900 mt-1">
                  {{ districts.length }}
                  <span class="text-sm font-normal text-slate-400">区</span>
                </p>
              </div>
              <div class="v-card-flat p-5 border-l-4 border-emerald-600">
                <p class="text-xs text-slate-500 uppercase tracking-tighter">
                  县级市
                </p>
                <p class="text-3xl font-black text-slate-900 mt-1">
                  {{ cities.length }}
                  <span class="text-sm font-normal text-slate-400">市</span>
                </p>
              </div>
              <div class="v-card-flat p-5 border-l-4 border-amber-500">
                <p class="text-xs text-slate-500 uppercase tracking-tighter">
                  市辖县
                </p>
                <p class="text-3xl font-black text-slate-900 mt-1">
                  {{ counties.length }}
                  <span class="text-sm font-normal text-slate-400">县</span>
                </p>
              </div>
            </div>

            <div class="space-y-12">
              
              <div v-if="districts.length">
                <div class="flex items-center justify-between gap-3 mb-5">
                  <h2 class="v-title-main !text-2xl !mt-0">中心城区</h2>
                  <button
                    class="v-btn v-tap-target text-xs"
                    @click="goToList('districts')"
                  >
                    查看全部
                  </button>
                </div>
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <article
                    v-for="item in previewList(districts)"
                    :key="`d-${item.id}`"
                    class="v-card v-touch-card overflow-hidden cursor-pointer"
                    @click="goToDetail(item)"
                  >
                    <img
                      :src="item.img"
                      :alt="item.title"
                      class="h-44 w-full object-cover"
                      loading="lazy"
                      decoding="async"
                    />
                    <div class="p-5">
                      <h3 class="text-lg font-bold text-slate-900">
                        {{ item.title }}
                      </h3>
                      <p
                        class="text-sm text-slate-500 mt-2 line-clamp-2 leading-relaxed"
                      >
                        {{ item.description }}
                      </p>
                    </div>
                  </article>
                </div>
              </div>

              
              <div v-if="cities.length">
                <div class="flex items-center justify-between gap-3 mb-5">
                  <h2 class="v-title-main !text-2xl !mt-0">特色县级市</h2>
                  <button
                    class="v-btn v-tap-target text-xs"
                    @click="goToList('cities')"
                  >
                    查看全部
                  </button>
                </div>
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <article
                    v-for="item in previewList(cities)"
                    :key="`c-${item.id}`"
                    class="relative v-touch-card h-56 rounded-2xl overflow-hidden cursor-pointer group"
                    @click="goToDetail(item)"
                  >
                    <img
                      :src="item.img"
                      :alt="item.title"
                      class="absolute inset-0 h-full w-full object-cover group-hover:scale-105 transition-transform duration-700"
                      loading="lazy"
                      decoding="async"
                    />
                    <div
                      class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"
                    ></div>
                    <div class="absolute bottom-0 left-0 p-5 text-white">
                      <h3 class="text-2xl font-bold">{{ item.title }}</h3>
                      <p
                        class="text-sm text-white/90 mt-1 line-clamp-1 font-light"
                      >
                        {{ item.description }}
                      </p>
                    </div>
                  </article>
                </div>
              </div>

              
              <div v-if="counties.length">
                <div class="flex items-center justify-between gap-3 mb-5">
                  <h2 class="v-title-main !text-2xl !mt-0">县域目的地</h2>
                  <button
                    class="v-btn v-tap-target text-xs"
                    @click="goToList('counties')"
                  >
                    查看全部
                  </button>
                </div>
                <div
                  class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5"
                >
                  <article
                    v-for="item in previewList(counties)"
                    :key="`x-${item.id}`"
                    class="v-card-flat v-touch-card p-4 flex gap-4 items-center cursor-pointer hover:border-slate-400 transition-colors"
                    @click="goToDetail(item)"
                  >
                    <img
                      :src="item.img"
                      :alt="item.title"
                      class="h-20 w-20 rounded-lg object-cover shadow-sm"
                      loading="lazy"
                      decoding="async"
                    />
                    <div class="min-w-0">
                      <h3 class="font-bold text-slate-900 truncate">
                        {{ item.title }}
                      </h3>
                      <p
                        class="text-xs text-slate-500 mt-1 line-clamp-2 leading-relaxed"
                      >
                        {{ item.description }}
                      </p>
                    </div>
                  </article>
                </div>
              </div>
            </div>
          </template>
        </section>

        
        <section
          id="go"
          class="v-section scroll-mt-44 md:scroll-mt-28 border-t border-gray-100 pt-16"
        >
          <div class="mb-8">
            <p class="v-title-eyebrow text-blue-600">Mobility Guide</p>
            <h2 class="v-title-main !text-2xl !mt-0">交通指南</h2>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <article
              v-for="item in trafficGuides"
              :key="item.id"
              class="v-card-flat p-6 hover:shadow-md transition-shadow"
            >
              <p
                class="text-[10px] tracking-[0.2em] text-blue-600 font-black uppercase"
              >
                {{ item.badge }}
              </p>
              <h3 class="text-xl font-bold text-slate-900 mt-2">
                {{ item.title }}
              </h3>
              <p class="text-sm text-slate-500 mt-3 leading-relaxed">
                {{ item.desc }}
              </p>
            </article>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<style scoped>

.mask-image-left {
  -webkit-mask-image: linear-gradient(
    to right,
    transparent,
    black 25%,
    black 100%
  );
  mask-image: linear-gradient(to right, transparent, black 25%, black 100%);
}

@media (max-width: 767px) {
  .mask-image-left {
    -webkit-mask-image: none;
    mask-image: none;
  }
}
</style>

