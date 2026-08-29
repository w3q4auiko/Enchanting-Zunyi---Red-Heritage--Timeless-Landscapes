<template>
  <div class="min-h-screen bg-[#f2ebe1] flex flex-col font-sans">
    <div
      v-if="loading"
      class="flex-grow flex justify-center items-center min-h-[400px]"
    >
      <div
        class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-800"
      ></div>
    </div>

    <main v-else class="flex-grow pb-16">
      <header class="relative w-full h-[400px] overflow-hidden group">
        <div
          :style="{ backgroundImage: `url('${bannerImage}')` }"
          class="absolute inset-0 bg-cover bg-center transition-transform duration-[3s] group-hover:scale-105"
        ></div>
        <div
          class="absolute inset-0 bg-gradient-to-t from-[#202724] via-[#202724]/40 to-transparent"
        ></div>

        <div
          class="absolute bottom-0 left-0 w-full p-6 md:p-12 text-white z-10"
        >
          <div
            class="max-w-7xl mx-auto flex flex-col md:flex-row items-end justify-between"
          >
            <div class="animate-fade-in-up">
              <span
                class="inline-block py-1 px-3 border border-white/30 bg-white/10 backdrop-blur-md rounded text-xs tracking-widest uppercase mb-4"
              >
                Region Profile
              </span>
              <h1 class="text-5xl md:text-7xl font-black tracking-tight mb-2">
                {{ info.name || info.title }}
              </h1>
              <p class="text-blue-200 text-lg md:text-xl font-light">
                遵义市下辖行政区划实体
              </p>
            </div>

            <div
              class="hidden md:block text-right opacity-80 animate-fade-in-up delay-100"
            >
              <div class="text-sm uppercase tracking-widest text-gray-400">
                Administrative Division
              </div>
              <div class="text-2xl font-bold">Zunyi, Guizhou</div>
            </div>
          </div>
        </div>
      </header>

      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8 relative z-20">
        <div class="flex flex-col lg:flex-row gap-8">
          <div class="lg:w-2/3">
            <div
              class="bg-white rounded-t-xl rounded-b-lg shadow-lg p-8 md:p-12 min-h-[500px]"
            >
              <div class="flex items-center mb-8 pb-4 border-b border-gray-100">
                <span
                  class="text-blue-600 font-bold text-lg tracking-widest uppercase mr-4"
                  >Introduction</span
                >
                <h2 class="text-2xl font-bold text-gray-900">区域概况</h2>
              </div>

              <div class="text-gray-600 leading-loose text-justify">
                <template v-for="(block, index) in contentBlocks" :key="index">
                  <h3
                    v-if="block.type === 'h3'"
                    class="text-xl font-bold text-gray-900 mt-10 mb-5 flex items-center"
                  >
                    <span
                      class="w-1.5 h-6 bg-blue-600 mr-3 rounded-full shadow-sm"
                    ></span>
                    {{ block.content }}
                  </h3>

                  <h4
                    v-else-if="block.type === 'h4'"
                    class="text-lg font-bold text-gray-800 mt-6 mb-3 ml-1"
                  >
                    {{ block.content }}
                  </h4>

                  <p v-else class="mb-4 indent-8">
                    {{ block.content }}
                  </p>
                </template>

                <p
                  v-if="contentBlocks.length === 0"
                  class="text-gray-400 italic text-center py-10"
                >
                  暂无详细介绍信息...
                </p>
              </div>

              <div
                v-if="info.image_url && info.image_url !== info.banner_url"
                class="mt-12 p-2 bg-gray-50 rounded-xl border border-gray-100"
              >
                <img
                  :src="info.image_url"
                  :alt="info.title"
                  class="w-full h-auto rounded-lg shadow-sm"
                  loading="lazy"
                  decoding="async"
                />
                <p class="text-center text-xs text-gray-400 mt-2">
                  区域自然或人文景观风貌展示
                </p>
              </div>
            </div>
          </div>

          <div class="lg:w-1/3 space-y-6">
            <div
              class="bg-white rounded-xl shadow-lg overflow-hidden sticky top-24"
            >
              <div class="bg-blue-900 p-4">
                <h3 class="text-white font-bold flex items-center">
                  <span class="mr-2">📍</span> 地理名片
                </h3>
              </div>

              <div class="h-[250px] w-full bg-gray-100 relative group">
                <div id="region-map" class="w-full h-full"></div>
                <div
                  v-if="!mapLoaded"
                  class="absolute inset-0 flex items-center justify-center text-gray-400 text-sm"
                >
                  地理空间数据同步中...
                </div>

                <a
                  @click="openNavigation"
                  class="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition flex items-center justify-center cursor-pointer"
                  title="调用外部导航引擎"
                ></a>
              </div>

              <div class="p-6">
                <ul class="space-y-4 text-sm">
                  <li
                    class="flex justify-between border-b border-gray-100 pb-3"
                  >
                    <span class="text-gray-500">行政管理级别</span>
                    <span class="font-bold text-gray-800">县级行政单位</span>
                  </li>
                  <li
                    class="flex justify-between border-b border-gray-100 pb-3"
                  >
                    <span class="text-gray-500">归属地级城市</span>
                    <span class="font-bold text-gray-800">中国 · 遵义</span>
                  </li>
                  <li class="flex flex-col gap-1">
                    <span class="text-gray-500">行政办公驻地</span>
                    <span
                      class="font-bold text-gray-800 text-right leading-relaxed"
                    >
                      {{ info.address || "坐标核实中" }}
                    </span>
                  </li>
                </ul>

                <button
                  @click="openNavigation"
                  class="w-full mt-6 py-2.5 bg-blue-50 text-blue-700 hover:bg-blue-100 font-bold rounded-lg transition flex items-center justify-center gap-2"
                >
                  <span>🗺️</span> 查阅详细位置
                </button>
              </div>
            </div>

            <div
              class="bg-white rounded-xl shadow p-6 text-center border-t-4 border-blue-600"
            >
              <p class="text-gray-500 text-sm mb-4">
                探索该行政区域内的核心旅游资源
              </p>
              <button
                @click="router.push('/highlights')"
                class="text-blue-600 font-medium hover:underline text-sm flex items-center justify-center w-full"
              >
                访问景点资源库 &rarr;
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
/**
 * 行政区域详情页组件。
 *
 * 负责加载区域详情、解析文本结构与地图展示，
 * 为全域导航与区域介绍提供可视化入口。
 */
import { ref, onMounted, computed, watch, nextTick } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getDetail } from "@/api/tourism";
import AMapLoader from "@amap/amap-jsapi-loader";

const AMAP_KEY = "fd112f8006337ad1a101ad6e3683fe2e";
const AMAP_SECURITY_CODE = "a9833532512ab69981676f8a6fc15ebc";

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const info = ref({});
const mapLoaded = ref(false);

let mapInstance = null;

/**
 * 详情页横幅图片计算。
 * @type {import("vue").ComputedRef<string>}
 */
const bannerImage = computed(
  () => info.value.banner_url || "/img/banner/default-region.jpg",
);

/**
 * 将区域描述拆解为分级结构块。
 * @type {import("vue").ComputedRef<Array<{type: string, content: string}>>}
 */
const contentBlocks = computed(() => {
  if (!info.value.description) return [];

  const lines = info.value.description
    .split("\n")
    .map((l) => l.trim())
    .filter((l) => l !== "");

  const blocks = [];

  const h3Regex = /^[一二三四五六七八九十]+、/;
  const h4Regex = /^(\d+\.|[①-⑩]|\(\d+\))/;

  lines.forEach((line) => {
    if (h3Regex.test(line)) {
      blocks.push({ type: "h3", content: line });
    } else if (h4Regex.test(line)) {
      blocks.push({ type: "h4", content: line });
    } else {
      blocks.push({ type: "p", content: line });
    }
  });

  return blocks;
});

/**
 * 拉取区域详情并初始化地图。
 * @returns {Promise<void>}
 */
const fetchDetail = async () => {
  loading.value = true;
  mapLoaded.value = false;
  try {
    const res = await getDetail(route.params.id, "region");
    if (res) {
      info.value = res;
      nextTick(() => initMap());
    }
  } catch (err) {
    console.error(
      "Critical Failure: Data acquisition pipeline terminated.",
      err,
    );
  } finally {
    loading.value = false;
  }
};

/**
 * 初始化区域地图。
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
    plugins: ["AMap.Marker"],
  })
    .then((AMap) => {
      mapInstance = new AMap.Map("region-map", {
        viewMode: "2D",
        zoom: 9,
        center: [info.value.longitude, info.value.latitude],
        mapStyle: "amap://styles/whitesmoke",
      });

      const marker = new AMap.Marker({
        position: [info.value.longitude, info.value.latitude],
        title: info.value.title,
      });
      mapInstance.add(marker);
      mapLoaded.value = true;
    })
    .catch((e) => {
      console.error("GIS Runtime Error: Map loader rejected.", e);
      mapLoaded.value = true;
    });
};

/**
 * 打开外部导航视图。
 * @returns {void}
 */
const openNavigation = () => {
  if (!info.value.latitude || !info.value.longitude) return;
  const { longitude, latitude } = info.value;
  const url = `https://uri.amap.com/view/map?center=${longitude},${latitude}&zoom=12&src=app&callnative=1`;
  window.open(url, "_blank");
};

onMounted(() => {
  fetchDetail();
});

watch(
  () => route.params.id,
  (newId, oldId) => {
    if (newId !== oldId) fetchDetail();
  },
);
</script>

<style scoped>
.animate-fade-in-up {
  animation: fadeInUp 0.8s ease-out forwards;
  opacity: 0;
  transform: translateY(20px);
}
.delay-100 {
  animation-delay: 0.2s;
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
