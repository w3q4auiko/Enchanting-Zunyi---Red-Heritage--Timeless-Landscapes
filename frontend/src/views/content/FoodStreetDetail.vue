<template>
  <div class="min-h-screen bg-[#FFFBF0] flex flex-col">
    <div
      v-if="loading"
      class="flex-grow flex justify-center items-center min-h-[400px]"
    >
      <div
        class="animate-spin rounded-full h-12 w-12 border-b-2 border-red-50"
      ></div>
    </div>

    <main v-else class="flex-grow w-full pb-16">
      <div class="relative w-full h-[60vh] min-h-[450px] overflow-hidden group">
        <div
          :style="{ backgroundImage: `url(${bannerImage})` }"
          class="absolute inset-0 bg-cover bg-center transition-transform duration-[2s] group-hover:scale-110"
        ></div>
        <div
          class="absolute inset-0 bg-gradient-to-t from-[#3E2723] via-[#3E2723]/60 to-transparent opacity-90"
        ></div>

        <div
          class="absolute bottom-0 left-0 w-full p-8 md:p-16 z-10 flex flex-col items-start"
        >
          <div class="flex items-center space-x-3 mb-4 animate-fade-in-up">
            <span
              class="px-3 py-1 bg-red-600 text-white text-xs font-bold rounded-full tracking-widest shadow-lg"
            >
              寻味街区
            </span>
          </div>

          <h1
            class="text-4xl md:text-6xl font-black text-white mb-4 drop-shadow-xl font-serif tracking-wide animate-fade-in-up delay-100"
          >
            {{ info.name }}
          </h1>

          <div
            class="w-24 h-1.5 bg-red-500 rounded-full mb-6 animate-fade-in-up delay-200"
          ></div>

          <p
            class="text-red-100 text-lg md:text-xl font-light max-w-2xl leading-relaxed animate-fade-in-up delay-300"
          >
            {{ info.alias || "汇聚地道烟火气息，品味遵义夜生活。" }}
          </p>
        </div>
      </div>

      <div class="max-w-6xl mx-auto -mt-12 relative z-20 px-4 sm:px-6">
        <div class="flex flex-col md:flex-row gap-8">
          <div class="md:w-2/3 space-y-8">
            <div
              class="bg-white rounded-2xl shadow-xl p-8 md:p-10 border border-red-50"
            >
              <div class="flex items-center mb-8 pb-4 border-b border-red-50">
                <span class="text-3xl mr-4">🏮</span>
                <h2 class="text-2xl font-bold text-gray-800">街区故事</h2>
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
                  暂无街区详细介绍...
                </p>
              </div>

              <div
                v-if="info.image_url && info.image_url !== info.banner_url"
                class="mt-10 rounded-xl overflow-hidden shadow-lg group cursor-pointer"
              >
                <img
                  :src="info.image_url"
                  :alt="info.name"
                  class="w-full h-auto object-cover group-hover:scale-105 transition duration-700"
                  loading="lazy"
                  decoding="async"
                />
              </div>
            </div>
          </div>

          <div class="md:w-1/3 space-y-6">
            <div
              class="bg-white rounded-2xl shadow-lg p-8 border-t-8 border-red-500 sticky top-24"
            >
              <h3
                class="text-lg font-bold text-gray-800 mb-6 flex justify-center uppercase tracking-widest text-red-900/50"
              >
                Street Info
              </h3>

              <div class="mb-8" v-if="recommendTags.length > 0">
                <div
                  class="text-xs text-gray-400 uppercase tracking-widest mb-3 text-center"
                >
                  🔥 必吃推荐
                </div>
                <div class="flex flex-wrap gap-2 justify-center">
                  <span
                    v-for="(tag, index) in recommendTags"
                    :key="index"
                    class="px-3 py-1.5 bg-red-50 text-red-600 rounded-lg text-sm font-medium border border-red-100"
                  >
                    {{ tag }}
                  </span>
                </div>
              </div>

              <div class="w-full h-px bg-gray-100 mb-6"></div>

              <div class="mb-8">
                <div
                  class="text-xs text-gray-400 uppercase tracking-widest mb-3 text-center"
                >
                  地理位置
                </div>
                <div class="bg-orange-50 rounded-xl p-4 flex items-start">
                  <div class="text-2xl mr-3 mt-1">📍</div>
                  <div>
                    <h4 class="font-bold text-gray-800 text-base leading-tight">
                      {{ info.address || "遵义市区" }}
                    </h4>
                  </div>
                </div>
              </div>

              <div class="space-y-3">
                <button
                  @click="openNavigation"
                  class="w-full py-3 bg-red-600 hover:bg-red-700 text-white rounded-xl shadow-lg hover:shadow-red-200 transition font-bold flex justify-center items-center gap-2"
                >
                  <span>🗺️</span> 导航前往
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
 * 美食街区详情页组件。
 *
 * 负责加载街区详情与推荐标签，输出街区故事与位置导航，
 * 支撑游客的街区探索体验。
 */
import { ref, onMounted, onBeforeUnmount, computed, watch } from "vue";
import { useRoute } from "vue-router";
import { getDetail } from "@/api/tourism";

const route = useRoute();

const loading = ref(true);
const info = ref({});
const previousTitle = ref("");

/**
 * 街区详情页横幅图片计算。
 * @type {import("vue").ComputedRef<string>}
 */
const bannerImage = computed(
  () => info.value.banner_url || "/img/banner/default-street.jpg",
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
 * 推荐美食标签解析。
 * @type {import("vue").ComputedRef<string[]>}
 */
const recommendTags = computed(() => {
  if (!info.value.recommend_tags) return [];
  return info.value.recommend_tags
    .split(/,|，/)
    .map((tag) => tag.trim())
    .filter((tag) => tag !== "");
});

/**
 * 拉取街区详情。
 * @returns {Promise<void>}
 */
const fetchDetail = async () => {
  loading.value = true;
  try {
    const res = await getDetail(route.params.id, "food_street");
    if (res) {
      info.value = res;
      document.title = `${res.name} - 寻味遵义`;
    }
  } catch (err) {
    console.error(
      "Infrastructure: Detail extraction process terminated abnormally.",
      err,
    );
  } finally {
    loading.value = false;
  }
};

/**
 * 打开导航搜索入口。
 * @returns {void}
 */
const openNavigation = () => {
  const query = `${info.value.name} ${info.value.address || ""}`;
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
.delay-300 {
  animation-delay: 0.3s;
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
