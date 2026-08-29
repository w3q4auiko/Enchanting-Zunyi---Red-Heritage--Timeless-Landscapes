<template>
  <div class="min-h-screen bg-[#FFFBF0] flex flex-col">
    <div
      v-if="loading"
      class="flex-grow flex justify-center items-center min-h-[400px]"
    >
      <div
        class="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"
      ></div>
    </div>

    <main v-else class="flex-grow w-full pb-16">
      <div class="relative w-full h-[60vh] min-h-[450px] overflow-hidden group">
        <div
          :style="{ backgroundImage: `url(${bannerImage})` }"
          class="absolute inset-0 bg-cover bg-center transition-transform duration-[2s] group-hover:scale-110"
        ></div>
        <div
          class="absolute inset-0 bg-gradient-to-t from-[#3E2723] via-transparent to-transparent opacity-90"
        ></div>

        <div
          class="absolute bottom-0 left-0 w-full p-8 md:p-16 z-10 flex flex-col items-start"
        >
          <div class="flex items-center space-x-3 mb-4 animate-fade-in-up">
            <span
              class="px-3 py-1 bg-orange-600 text-white text-xs font-bold rounded-full tracking-widest shadow-lg"
            >
              {{ info.category }}
            </span>
          </div>

          <h1
            class="text-4xl md:text-6xl font-black text-white mb-6 drop-shadow-xl font-serif tracking-wide animate-fade-in-up delay-100"
          >
            {{ info.title }}
          </h1>

          <div
            class="w-24 h-1.5 bg-orange-500 rounded-full mb-6 animate-fade-in-up delay-200"
          ></div>

          <p
            class="text-orange-100 text-lg md:text-xl font-light max-w-2xl leading-relaxed animate-fade-in-up delay-300"
          >
            {{ info.slogan }}
          </p>
        </div>
      </div>

      <div class="max-w-6xl mx-auto -mt-12 relative z-20 px-4 sm:px-6">
        <div class="flex flex-col md:flex-row gap-8">
          <div class="md:w-2/3 space-y-8">
            <div
              class="bg-white rounded-2xl shadow-xl p-8 md:p-10 border border-orange-100"
            >
              <div
                class="flex items-center mb-8 pb-4 border-b border-orange-100"
              >
                <span class="text-3xl mr-4">🥘</span>
                <h2 class="text-2xl font-bold text-gray-800">风味溯源</h2>
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
                  暂无详细介绍...
                </p>
              </div>

              <div
                v-if="info.tips"
                class="mt-10 bg-[#FFF3E0] border-l-4 border-orange-500 p-6 rounded-r-xl"
              >
                <h3
                  class="font-bold text-orange-900 mb-2 flex items-center text-lg"
                >
                  <span class="mr-2 text-xl">💡</span> 赏味贴士
                </h3>
                <p class="text-orange-800 leading-relaxed">{{ info.tips }}</p>
              </div>
            </div>

            <div
              v-if="relatedFoods.length > 0"
              class="mt-12 pt-10 border-t border-orange-100"
            >
              <h3
                class="text-2xl font-bold text-gray-800 mb-6 flex items-center"
              >
                <span class="text-3xl mr-3">✨</span> 猜你喜欢
              </h3>
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
                <div
                  v-for="item in relatedFoods"
                  :key="item.id"
                  @click="router.push(`/attraction/food/${item.id}`)"
                  class="bg-white rounded-xl overflow-hidden shadow-md cursor-pointer hover:shadow-xl transition duration-300 group"
                >
                  <div class="h-32 overflow-hidden relative">
                    <img
                      :src="
                        item.image_url ||
                        item.banner_url ||
                        '/img/overview_hero.jpg'
                      "
                      :alt="item.name"
                      class="w-full h-full object-cover group-hover:scale-110 transition duration-500"
                      loading="lazy"
                      decoding="async"
                    />
                  </div>
                  <div class="p-4">
                    <h4
                      class="font-bold text-gray-800 group-hover:text-orange-600 transition truncate"
                    >
                      {{ item.name }}
                    </h4>
                    <p class="text-xs text-gray-500 mt-1 line-clamp-1">
                      {{ item.tips || "去尝尝正宗的味道" }}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div class="text-center pt-8">
              <router-link
                to="/taste"
                class="text-orange-600 hover:text-orange-800 font-medium inline-flex items-center transition"
              >
                浏览更多遵义美食 <span class="ml-2">→</span>
              </router-link>
            </div>
          </div>

          <div class="md:w-1/3 space-y-6">
            <div
              class="bg-white rounded-2xl shadow-lg p-8 border-t-8 border-orange-500 sticky top-24"
            >
              <h3
                class="text-lg font-bold text-gray-800 mb-8 flex justify-center uppercase tracking-widest text-orange-900/50"
              >
                Dining Info
              </h3>

              <div class="space-y-8">
                <div class="text-center">
                  <div
                    class="text-xs text-gray-400 uppercase tracking-widest mb-2"
                  >
                    人均消费
                  </div>
                  <div class="text-4xl font-black text-red-600 font-serif">
                    {{ displayPrice }}
                  </div>
                </div>

                <div class="w-full h-px bg-gray-100"></div>

                <div>
                  <div
                    class="text-xs text-gray-400 uppercase tracking-widest mb-3 text-center"
                  >
                    推荐打卡
                  </div>
                  <div class="bg-orange-50 rounded-xl p-4 flex items-start">
                    <div class="text-2xl mr-3 mt-1">📍</div>
                    <div>
                      <h4
                        class="font-bold text-gray-800 text-lg leading-tight mb-1"
                      >
                        {{
                          info.recommend_shop || info.address || "暂无特定店铺"
                        }}
                      </h4>
                      <p
                        class="text-xs text-gray-500"
                        v-if="info.address && info.recommend_shop"
                      >
                        {{ info.address }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div class="mt-10 space-y-3">
                <button
                  @click="openNavigation"
                  class="w-full py-3 bg-orange-600 hover:bg-orange-700 text-white rounded-xl shadow-lg hover:shadow-orange-200 transition font-bold flex justify-center items-center gap-2"
                >
                  <span>🗺️</span> 导航前往
                </button>
                <button
                  class="w-full py-3 bg-white border border-gray-200 text-gray-500 hover:bg-gray-50 rounded-xl transition font-medium text-sm flex justify-center items-center gap-2"
                >
                  <span>❤️</span> 想吃 (收藏)
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
 * 美食详情页组件。
 *
 * 负责加载美食详情与同类推荐，提供风味故事与导航入口，
 * 强化游客对遵义美食的探索体验。
 */
import { ref, onMounted, onBeforeUnmount, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getDetail, getFoods } from "@/api/tourism";

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const info = ref({});
const relatedFoods = ref([]);
const previousTitle = ref("");

/**
 * 美食详情页横幅图片计算。
 * @type {import("vue").ComputedRef<string>}
 */
const bannerImage = computed(
  () => info.value.banner_url || "/img/banner/default-food.jpg",
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
 * 统一人均价格展示。
 * @type {import("vue").ComputedRef<string>}
 */
const displayPrice = computed(() => {
  const price = info.value.ticket_info || info.value.price;
  if (!price || price === "免费") return "丰俭由人";
  if (/\d/.test(price) && !price.includes("¥") && !price.includes("元")) {
    return `¥${price}`;
  }
  return price;
});

/**
 * 拉取美食详情与同类推荐。
 * @returns {Promise<void>}
 */
const fetchDetail = async () => {
  loading.value = true;
  try {
    const res = await getDetail(route.params.id, "food");
    if (res) {
      info.value = res;
      document.title = `${res.title} - 醉美遵义 · 山河红韵`;

      if (res.category) {
        const relatedRes = await getFoods(res.category);
        if (Array.isArray(relatedRes)) {
          relatedFoods.value = relatedRes
            .filter((item) => item.id !== res.id)
            .slice(0, 3);
        }
      }
    }
  } catch (err) {
    console.error("Critical: Analytics data sync failed.", err);
  } finally {
    loading.value = false;
  }
};

/**
 * 打开导航搜索入口。
 * @returns {void}
 */
const openNavigation = () => {
  const query = `${info.value.title} ${info.value.recommend_shop || ""}`;
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
