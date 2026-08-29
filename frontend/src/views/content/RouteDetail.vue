<template>
  <div class="min-h-screen bg-[#F9FAFB] flex flex-col">
    <div
      v-if="loading"
      class="flex-grow flex justify-center items-center min-h-[400px]"
    >
      <div
        class="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"
      ></div>
    </div>

    <main v-else class="flex-grow w-full pb-16">
      <div class="relative w-full h-[60vh] min-h-[450px] overflow-hidden group">
        <div
          :style="{ backgroundImage: `url(${bannerImage})` }"
          class="absolute inset-0 bg-cover bg-center transition-transform duration-[2s] group-hover:scale-110"
        ></div>
        <div
          class="absolute inset-0 bg-gradient-to-t from-[#1F2937] via-transparent to-transparent opacity-90"
        ></div>

        <div
          class="absolute bottom-0 left-0 w-full p-8 md:p-16 z-10 flex flex-col items-start"
        >
          <div class="flex items-center space-x-3 mb-4 animate-fade-in-up">
            <span
              class="px-3 py-1 bg-emerald-600 text-white text-xs font-bold rounded-full tracking-widest shadow-lg"
            >
              {{ info.category || "达人路线" }}
            </span>
            <span
              class="px-3 py-1 bg-white/20 backdrop-blur-md text-white text-xs font-bold rounded-full"
            >
              难度系数：{{ "★".repeat(info.difficulty || 1)
              }}{{ "☆".repeat(5 - (info.difficulty || 1)) }}
            </span>
          </div>

          <h1
            class="text-4xl md:text-6xl font-black text-white mb-6 drop-shadow-xl font-sans tracking-wide animate-fade-in-up delay-100"
          >
            {{ info.title }}
          </h1>

          <div
            class="w-24 h-1.5 bg-emerald-500 rounded-full mb-6 animate-fade-in-up delay-200"
          ></div>
        </div>
      </div>

      <div class="max-w-6xl mx-auto -mt-12 relative z-20 px-4 sm:px-6">
        <div class="flex flex-col md:flex-row gap-8">
          <div class="md:w-2/3 space-y-8">
            <div
              class="bg-white rounded-2xl shadow-xl p-8 md:p-10 border border-gray-100"
            >
              <div class="flex items-center mb-8 pb-4 border-b border-gray-100">
                <span class="text-3xl mr-4">🥾</span>
                <h2 class="text-2xl font-bold text-gray-800">路线规划详情</h2>
              </div>

              <div
                class="prose max-w-none text-gray-600 leading-loose text-justify text-lg"
              >
                <p
                  v-for="(paragraph, index) in formattedDescription"
                  :key="index"
                  class="mb-6 indent-8"
                >
                  {{ paragraph }}
                </p>
                <p
                  v-if="!info.description"
                  class="text-gray-400 italic text-center"
                >
                  暂无详细路线说明...
                </p>
              </div>

              <div
                v-if="info.image_url && info.image_url !== info.banner_url"
                class="mt-10 rounded-xl overflow-hidden shadow-lg group cursor-pointer"
              >
                <img
                  :src="info.image_url"
                  :alt="info.title"
                  class="w-full h-auto object-cover group-hover:scale-105 transition duration-700"
                  loading="lazy"
                  decoding="async"
                />
              </div>

              <div
                v-if="info.tips"
                class="mt-10 bg-emerald-50 border-l-4 border-emerald-500 p-6 rounded-r-xl"
              >
                <h3
                  class="font-bold text-emerald-900 mb-2 flex items-center text-lg"
                >
                  <span class="mr-2 text-xl">⚠️</span> 安全游玩提示
                </h3>
                <p class="text-emerald-800 leading-relaxed">{{ info.tips }}</p>
              </div>
            </div>
          </div>

          <div class="md:w-1/3 space-y-6">
            <div
              class="bg-white rounded-2xl shadow-lg p-8 border-t-8 border-emerald-500 sticky top-24"
            >
              <h3
                class="text-lg font-bold text-gray-800 mb-6 flex justify-center uppercase tracking-widest text-emerald-900/50"
              >
                Route Indicators
              </h3>

              <div class="grid grid-cols-2 gap-4 mb-6">
                <div class="bg-gray-50 p-4 rounded-xl text-center">
                  <div class="text-xs text-gray-400 uppercase mb-1">
                    轨迹里程
                  </div>
                  <div class="text-2xl font-black text-gray-800">
                    {{ info.distance_km || "--"
                    }}<span class="text-sm font-normal text-gray-500 ml-1"
                      >km</span
                    >
                  </div>
                </div>
                <div class="bg-gray-50 p-4 rounded-xl text-center">
                  <div class="text-xs text-gray-400 uppercase mb-1">
                    预计耗时
                  </div>
                  <div class="text-2xl font-black text-gray-800">
                    {{ info.duration_hours || "--"
                    }}<span class="text-sm font-normal text-gray-500 ml-1"
                      >h</span
                    >
                  </div>
                </div>
                <div class="bg-gray-50 p-4 rounded-xl text-center">
                  <div class="text-xs text-gray-400 uppercase mb-1">
                    累计爬升
                  </div>
                  <div class="text-2xl font-black text-gray-800">
                    {{ info.climb_meters || "--"
                    }}<span class="text-sm font-normal text-gray-500 ml-1"
                      >m</span
                    >
                  </div>
                </div>
                <div class="bg-gray-50 p-4 rounded-xl text-center">
                  <div class="text-xs text-gray-400 uppercase mb-1">
                    闭环类型
                  </div>
                  <div class="text-lg font-bold text-gray-800 mt-1">
                    {{ info.route_type || "常规线" }}
                  </div>
                </div>
              </div>

              <div class="w-full h-px bg-gray-100 mb-6"></div>

              <div class="mb-8">
                <div
                  class="text-xs text-gray-400 uppercase tracking-widest mb-3"
                >
                  徒步/集结起点
                </div>
                <div
                  class="flex items-start bg-emerald-50/50 p-3 rounded-lg border border-emerald-100"
                >
                  <span class="text-xl mr-2 mt-0.5">📍</span>
                  <div>
                    <h4 class="font-bold text-gray-800 text-md">
                      {{ info.start_point || info.address || "坐标核实中" }}
                    </h4>
                    <p
                      class="text-xs text-gray-500 mt-1"
                      v-if="info.address && info.start_point"
                    >
                      {{ info.address }}
                    </p>
                  </div>
                </div>
              </div>

              <div class="space-y-3">
                <button
                  @click="openNavigation"
                  class="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl shadow-lg transition font-bold flex justify-center items-center gap-2"
                >
                  <span>🗺️</span> 一键导航至起点
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
/**
 * 旅游路线详情页组件。
 *
 * 负责加载路线详情与导航入口，展示路线难度、里程与
 * 起点信息，支撑游客徒步规划。
 */
import { ref, onMounted, onBeforeUnmount, computed, watch } from "vue";
import { useRoute } from "vue-router";
import { getDetail } from "@/api/tourism";

const route = useRoute();

const loading = ref(true);
const info = ref({});
const previousTitle = ref("");

/**
 * 路线详情页横幅图片计算。
 * @type {import("vue").ComputedRef<string>}
 */
const bannerImage = computed(
  () => info.value.banner_url || "/img/banner/default-route.jpg",
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
 * 拉取路线详情。
 * @returns {Promise<void>}
 */
const fetchDetail = async () => {
  loading.value = true;
  try {
    const res = await getDetail(route.params.id, "route");
    if (res) {
      info.value = res;
      document.title = `${res.title} - 精选路线`;
    }
  } catch (err) {
    console.error("Data Pipeline Error: Failed to hydrate route entity.", err);
  } finally {
    loading.value = false;
  }
};

/**
 * 打开路线起点导航搜索。
 * @returns {void}
 */
const openNavigation = () => {
  const query = info.value.start_point || info.value.title;
  const url = `https://uri.amap.com/search?keyword=${encodeURIComponent(query)}&mode=car&callnative=1`;
  window.open(url, "_blank");
};

onMounted(() => {
  previousTitle.value = document.title;
  fetchDetail();
});

onBeforeUnmount(() => {
  document.title = previousTitle.value || "醉美遵义 · 山河红韵";
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
  animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  opacity: 0;
  transform: translateY(20px);
}
.delay-100 {
  animation-delay: 0.1s;
}
.delay-200 {
  animation-delay: 0.2s;
}

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.indent-8 {
  text-indent: 2em;
}
</style>
