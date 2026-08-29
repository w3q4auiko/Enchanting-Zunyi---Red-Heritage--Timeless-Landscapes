<script setup>
/**
 * 景点详情页组件。
 *
 * 负责加载景点详情、地图定位与周边推荐，提供游客
 * 深度了解景点与导航的完整入口。
 */
import {
  ref,
  onMounted,
  computed,
  watch,
  nextTick,
  onBeforeUnmount,
} from "vue";
import { useRoute, useRouter } from "vue-router";
import { getDetail, getAttractions } from "@/api/tourism";
import AMapLoader from "@amap/amap-jsapi-loader";

/**
 * 高德地图前端密钥。
 * @type {string}
 */
const AMAP_KEY = "fd112f8006337ad1a101ad6e3683fe2e";
/**
 * 高德地图安全码。
 * @type {string}
 */
const AMAP_SECURITY_CODE = "a9833532512ab69981676f8a6fc15ebc";

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const info = ref({});
const mapLoaded = ref(false);
const relatedLoading = ref(false);
const relatedItems = ref([]);
let mapInstance = null;
const previousTitle = ref("");

/**
 * 详情页横幅图片计算。
 * @type {import("vue").ComputedRef<string>}
 */
const bannerImage = computed(
  () => info.value.banner_url || "/img/banner/default-scenery.jpg",
);

/**
 * 详情正文段落拆分。
 * @type {import("vue").ComputedRef<string[]>}
 */
const formattedDescription = computed(() =>
  info.value.description
    ? info.value.description.split("\n").filter((p) => p.trim() !== "")
    : [],
);

/**
 * 拉取景点详情并初始化地图与推荐。
 * @returns {Promise<void>}
 */
const fetchDetail = async () => {
  loading.value = true;
  mapLoaded.value = false;

  try {
    const id = route.params.id;
    const res = await getDetail(id, "attraction");

    if (res) {
      info.value = res;
      document.title = `${res.title} - 醉美遵义 · 山河红韵`;

      nextTick(() => {
        initMap();
        fetchRelated();
      });
    }
  } catch (err) {
    console.error("Detail retrieval failed:", err);
  } finally {
    loading.value = false;
  }
};

/**
 * 拉取周边推荐景点。
 * @returns {Promise<void>}
 */
const fetchRelated = async () => {
  relatedLoading.value = true;
  try {
    const res = await getAttractions();
    if (res && Array.isArray(res)) {
      relatedItems.value = res
        .filter((item) => item.id != info.value.id)
        .sort(() => 0.5 - Math.random())
        .slice(0, 3);
    }
  } catch (e) {
    console.warn("Related items fetch failed", e);
  } finally {
    relatedLoading.value = false;
  }
};

/**
 * 打开高德导航。
 * @returns {void}
 */
const openNavigation = () => {
  if (!info.value.latitude || !info.value.longitude) {
    alert("该地点暂无精确位置信息，请尝试复制地址搜索");
    return;
  }
  const { longitude, latitude, title } = info.value;
  const url = `https://uri.amap.com/navigation?to=${longitude},${latitude},${title}&mode=car&callnative=1`;
  window.open(url, "_blank");
};

/**
 * 初始化高德地图实例。
 * @returns {void}
 */
const initMap = () => {
  if (!info.value.latitude || !info.value.longitude) {
    mapLoaded.value = true;
    return;
  }

  if (mapInstance) {
    mapInstance.destroy();
    mapInstance = null;
  }

  window._AMapSecurityConfig = { securityJsCode: AMAP_SECURITY_CODE };

  AMapLoader.load({
    key: AMAP_KEY,
    version: "2.0",
    plugins: ["AMap.ToolBar", "AMap.Marker"],
  })
    .then((AMap) => {
      mapInstance = new AMap.Map("map-container", {
        viewMode: "3D",
        zoom: 15,
        center: [info.value.longitude, info.value.latitude],
        mapStyle: "amap://styles/normal",
      });

      const marker = new AMap.Marker({
        position: [info.value.longitude, info.value.latitude],
        title: info.value.title,
      });
      mapInstance.add(marker);
      mapLoaded.value = true;
    })
    .catch((e) => {
      console.error("AMap load failed:", e);
      mapLoaded.value = true;
    });
};

/**
 * 跳转到指定景点详情。
 * @param {number} id - 景点主键。
 * @returns {void}
 */
const goToDetail = (id) => {
  router.push(`/attraction/scenery/${id}`);
};

onMounted(() => {
  previousTitle.value = document.title;
  fetchDetail();
});

onBeforeUnmount(() => {
  if (mapInstance) {
    mapInstance.destroy();
    mapInstance = null;
  }
  document.title = previousTitle.value || "醉美遵义 · 山河红韵";
});

watch(
  () => route.params.id,
  (newId, oldId) => {
    if (newId !== oldId) {
      fetchDetail();
    }
  },
);
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <div
      v-if="loading"
      class="flex-grow flex justify-center items-center min-h-[400px]"
    >
      <div
        class="animate-spin rounded-full h-12 w-12 border-b-2 border-red-700"
      ></div>
    </div>

    <main v-else class="flex-grow w-full pb-16">
      <div class="relative w-full h-[50vh] min-h-[400px] overflow-hidden group">
        <div
          :style="{ backgroundImage: `url(${bannerImage})` }"
          class="absolute inset-0 bg-cover bg-center transition-transform duration-1000 group-hover:scale-105"
        ></div>
        <div
          class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent"
        ></div>

        <div
          class="relative z-10 max-w-7xl mx-auto h-full flex flex-col justify-end pb-12 px-4 sm:px-6 lg:px-8 animate-fade-in-up"
        >
          <div class="flex items-center space-x-3 mb-4">
            <span
              class="py-1 px-3 rounded bg-red-700 text-white text-xs font-bold tracking-wider uppercase shadow-sm"
            >
              {{ info.category || "热门景点" }}
            </span>
            <span
              v-if="info.status === 1"
              class="py-1 px-3 rounded bg-green-600 text-white text-xs font-bold shadow-sm"
            >
              开放中
            </span>
          </div>

          <h1
            class="text-4xl md:text-6xl font-extrabold text-white tracking-wide mb-4 drop-shadow-lg font-serif"
          >
            {{ info.title }}
          </h1>

          <div class="w-20 h-1 bg-red-600 mb-6"></div>

          <p
            v-if="info.slogan"
            class="text-lg md:text-xl text-gray-200 italic font-light max-w-2xl"
          >
            “{{ info.slogan }}”
          </p>
        </div>
      </div>

      <div class="max-w-7xl mx-auto -mt-16 relative z-20 px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col lg:flex-row gap-8">
          <div class="lg:w-1/3 order-2 lg:order-2 space-y-6">
            <div
              class="bg-white rounded-xl shadow-xl p-6 border-t-4 border-red-700"
            >
              <h3
                class="text-xl font-bold text-gray-800 mb-6 flex items-center border-b pb-4"
              >
                <span>🎫 参观指南</span>
              </h3>

              <ul class="space-y-6 text-gray-600">
                <li class="flex items-start">
                  <div
                    class="flex-shrink-0 w-10 h-10 rounded-full bg-red-50 flex items-center justify-center text-red-600 mr-4 text-xl"
                  >
                    ¥
                  </div>
                  <div>
                    <span
                      class="block text-xs text-gray-400 mb-1 uppercase tracking-wider"
                      >门票价格</span
                    >
                    <span class="text-2xl font-bold text-red-600">
                      {{ info.ticket_info || "免费" }}
                    </span>
                  </div>
                </li>

                <li class="flex items-start">
                  <div
                    class="flex-shrink-0 w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center text-blue-600 mr-4 text-xl"
                  >
                    🕒
                  </div>
                  <div>
                    <span
                      class="block text-xs text-gray-400 mb-1 uppercase tracking-wider"
                      >开放时间</span
                    >
                    <span class="text-sm font-medium text-gray-800 leading-6">
                      {{ info.opening_hours || "全天开放" }}
                    </span>
                  </div>
                </li>

                <li class="flex items-start">
                  <div
                    class="flex-shrink-0 w-10 h-10 rounded-full bg-green-50 flex items-center justify-center text-green-600 mr-4 text-xl"
                  >
                    📍
                  </div>
                  <div>
                    <span
                      class="block text-xs text-gray-400 mb-1 uppercase tracking-wider"
                      >景点地址</span
                    >
                    <span
                      class="text-sm font-medium text-gray-800 leading-tight block"
                    >
                      {{ info.address || "暂无详细地址信息" }}
                    </span>
                  </div>
                </li>
              </ul>

              <div class="mt-8 pt-6 border-t border-gray-100 grid gap-3">
                <button
                  class="w-full py-3 bg-red-700 hover:bg-red-800 text-white rounded-lg transition shadow-md font-bold flex justify-center items-center gap-2 group"
                  @click="openNavigation"
                >
                  <span class="group-hover:scale-110 transition-transform"
                    >🧭</span
                  >
                  一键导航
                </button>
              </div>
            </div>

            <div class="bg-white rounded-xl shadow-md p-1 overflow-hidden">
              <div
                id="map-container"
                class="w-full h-[300px] rounded-lg bg-gray-100 relative"
              >
                <div
                  v-if="!mapLoaded"
                  class="absolute inset-0 flex items-center justify-center text-gray-400 text-sm"
                >
                  <span class="animate-pulse">地图加载中...</span>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-xl shadow-md p-6">
              <h3
                class="text-base font-bold text-gray-800 mb-4 flex justify-between items-center"
              >
                <span>周边推荐</span>
              </h3>
              <div v-if="relatedLoading" class="flex justify-center py-4">
                <div
                  class="animate-spin h-5 w-5 border-2 border-gray-300 rounded-full border-t-red-600"
                ></div>
              </div>
              <div v-else class="space-y-3">
                <div
                  v-for="item in relatedItems"
                  :key="item.id"
                  class="flex gap-3 p-2 hover:bg-gray-50 rounded-lg cursor-pointer transition group"
                  @click="goToDetail(item.id)"
                >
                  <div
                    class="w-16 h-16 rounded overflow-hidden flex-shrink-0 bg-gray-200"
                  >
                    <img
                      :src="item.image_url"
                      class="w-full h-full object-cover group-hover:scale-110 transition duration-500"
                      :alt="item.title || '推荐景点图片'"
                      loading="lazy"
                      decoding="async"
                    />
                  </div>
                  <div class="flex-grow">
                    <h4
                      class="text-sm font-bold text-gray-800 group-hover:text-red-700 line-clamp-1"
                    >
                      {{ item.title }}
                    </h4>
                    <p class="text-xs text-gray-500 mt-1 line-clamp-2">
                      {{ item.description }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="lg:w-2/3 order-1 lg:order-1 space-y-8">
            <div class="bg-white rounded-xl shadow-sm p-8 min-h-[500px]">
              <div class="flex items-center mb-8">
                <div class="w-1.5 h-8 bg-red-700 mr-4 rounded-full"></div>
                <h2 class="text-2xl font-bold text-gray-800">景点概况</h2>
              </div>

              <div
                class="prose prose-lg max-w-none text-gray-600 leading-loose text-justify"
              >
                <p
                  v-for="(paragraph, index) in formattedDescription"
                  :key="index"
                  class="mb-4 indent-8"
                >
                  {{ paragraph }}
                </p>
                <p
                  v-if="!info.description"
                  class="text-gray-400 italic text-center py-8 bg-gray-50 rounded-lg"
                >
                  暂无详细描述信息...
                </p>
              </div>

              <div
                v-if="info.image_url && info.image_url !== info.banner_url"
                class="mt-10 rounded-xl overflow-hidden shadow-lg"
              >
                <img
                  :src="info.image_url"
                  class="w-full h-auto object-cover hover:scale-[1.02] transition duration-700"
                  :alt="info.title ? info.title + ' 实景图' : '景点图片'"
                  loading="lazy"
                  decoding="async"
                />
              </div>
              <p
                v-if="info.image_caption"
                class="text-center text-gray-500 text-sm mt-3 italic"
              >
                {{ info.image_caption }}
              </p>
              <div
                v-if="info.tips"
                class="mt-12 bg-orange-50 border-l-4 border-orange-400 p-6 rounded-r-xl"
              >
                <h3
                  class="text-lg font-bold text-orange-800 mb-3 flex items-center"
                >
                  <span class="mr-2">💡</span> 游玩小贴士
                </h3>
                <p class="text-base text-orange-700 leading-relaxed">
                  {{ info.tips }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.animate-fade-in-up {
  animation: fadeInUp 0.8s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.indent-8 {
  text-indent: 2em;
}
</style>
