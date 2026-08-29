<script setup>
/**
 * 首页展示组件。
 *
 * 聚合轮播视觉入口与三大主题分区导航，承担游客进入
 * 遵义旅游信息系统的首屏导览职责。
 */
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRouter } from "vue-router";
import { fixUrl } from "@/utils/common.js";
import { getBanners } from "@/api/tourism";
import themeHistoryUrl from "@/assets/images/home/theme-history-zine.webp";
import themeNatureUrl from "@/assets/images/home/theme-nature-zine.webp";
import themeSpiritUrl from "@/assets/images/home/theme-spirit-zine.webp";

const router = useRouter();

const currentBannerIndex = ref(0);
const bannerTimer = ref(null);
const fallbackBanners = [
  {
    id: "fallback-hero",
    img: themeHistoryUrl,
    title: "红城印象",
    desc: "在遵义的历史脉络中，寻见山河与人文交织的起点。",
    url: "/overview",
  },
];

const banners = ref(fallbackBanners);

/**
 * 拉取并规范化轮播数据。
 * @returns {Promise<void>}
 */
const fetchBannersData = async () => {
  try {
    const data = await getBanners();
    const normalized = (Array.isArray(data) ? data : []).map((item) => {
      const url1 = item.banner_url ? fixUrl(item.banner_url) : "";
      const url2 = item.image_url ? fixUrl(item.image_url) : "";
      const finalImg = url1 || url2;
      const type = item.entity_type || "scenery";

      return {
        id: item.id,
        img: finalImg,
        title: item.title,
        desc: item.description,
        url: `/attraction/${type}/${item.id}`,
      };
    });

    banners.value = normalized.length ? normalized : fallbackBanners;
    currentBannerIndex.value = 0;
    startAutoPlay();
  } catch (error) {
    console.error("Critical: Failed to load banner data.", error);
    banners.value = fallbackBanners;
  }
};

/**
 * 当前轮播数据的计算视图。
 * @type {import("vue").ComputedRef<object>}
 */
const currentBanner = computed(() => {
  if (!banners.value.length) return { title: "", desc: "", img: "" };
  return banners.value[currentBannerIndex.value];
});

/**
 * 启动轮播自动播放。
 * @returns {void}
 */
const startAutoPlay = () => {
  if (banners.value.length <= 1) return;
  stopAutoPlay();
  bannerTimer.value = setInterval(() => {
    currentBannerIndex.value =
      (currentBannerIndex.value + 1) % banners.value.length;
  }, 7500);
};

/**
 * 停止轮播自动播放。
 * @returns {void}
 */
const stopAutoPlay = () => {
  if (bannerTimer.value) clearInterval(bannerTimer.value);
};

onMounted(fetchBannersData);
onUnmounted(stopAutoPlay);
</script>

<template>
  <div class="page-wrapper flex flex-col min-h-screen">
    <main class="w-full flex-grow">
      <section
        id="hero-banner"
        class="relative w-full overflow-hidden"
        @mouseenter="stopAutoPlay"
        @mouseleave="startAutoPlay"
      >
        <div
          v-if="banners.length > 0"
          class="banner-container h-full relative bg-gray-900"
        >
          <div
            v-for="(banner, index) in banners"
            :key="banner.id"
            :class="[
              currentBannerIndex === index
                ? 'opacity-100 z-10'
                : 'opacity-0 z-0 pointer-events-none',
            ]"
            class="absolute inset-0 h-full w-full transition-opacity duration-1000 ease-in-out cursor-pointer"
            @click="router.push(banner.url)"
          >
            <img
              :alt="banner.title"
              :src="banner.img"
              :loading="currentBannerIndex === index ? 'eager' : 'lazy'"
              :fetchpriority="currentBannerIndex === index ? 'high' : 'low'"
              decoding="async"
              width="1920"
              height="680"
              class="h-full w-full object-cover will-change-transform"
              @error="$event.target.style.display = 'none'"
            />
            <div
              class="absolute inset-0 bg-gradient-to-r from-red-900/80 to-gray-900/60 -z-10"
            ></div>
            <div class="absolute inset-0 bg-black/20"></div>
          </div>
        </div>

        <div
          id="navi_left"
          class="absolute inset-0 flex flex-col justify-center items-center p-4 pointer-events-none z-20"
        >
          <div v-if="banners.length > 0" class="text-center">
            <h1
              :key="currentBanner.id"
              class="text-5xl md:text-6xl font-extrabold mb-4 text-white drop-shadow-lg slide-up-animation"
            >
              {{ currentBanner.title }}
            </h1>
            <p
              :key="currentBanner.id + '-desc'"
              class="text-xl md:text-2xl text-white/90 drop-shadow-md slide-up-animation"
              style="animation-delay: 0.2s"
            >
              {{ currentBanner.desc }}
            </p>
          </div>
        </div>

        <div
          v-if="banners.length > 0"
          class="banner-dots absolute bottom-8 left-1/2 transform -translate-x-1/2 flex space-x-2 z-30"
        >
          <button
            v-for="(banner, index) in banners"
            :key="'dot-' + index"
            class="p-2 group focus:outline-none"
            :aria-label="`切换到第 ${index + 1} 张图片`"
            :aria-current="currentBannerIndex === index ? 'true' : 'false'"
            @click="currentBannerIndex = index"
          >
            <div
              :class="[
                'dot w-3 h-3 rounded-full transition-all duration-300 shadow-md',
                currentBannerIndex === index
                  ? 'active-dot bg-white scale-125'
                  : 'bg-white/50 group-hover:bg-white/80',
              ]"
            ></div>
          </button>
        </div>
      </section>

      <div id="content" class="w-full bg-[#fcfaf5] overflow-hidden relative">
        <div class="z-bg-text">ZUNYI</div>

        <section class="max-w-[1280px] mx-auto px-6 py-24 relative z-10">
          <div
            class="flex flex-col md:flex-row items-end justify-between mb-24 border-b border-gray-200 pb-8"
          >
            <div class="max-w-xl">
              <h2
                class="text-4xl md:text-5xl font-serif font-bold text-gray-900 mb-4"
              >
                红城胜景 <span class="text-[#a61f2d] italic">·</span> 醉美遵义
              </h2>
              <p class="text-gray-500 text-lg font-light">
                以历史、山水与精神为三重维度，构建遵义城市叙事的可视化索引。
              </p>
            </div>
            <div
              class="hidden md:block text-[#a61f2d] font-bold tracking-widest uppercase text-sm"
            >
              Select Collection 2026
            </div>
          </div>

          <div
            class="relative group mb-32 md:mb-40 cursor-pointer"
            @click="router.push('/overview')"
          >
            <div class="flex flex-col md:flex-row items-center">
              <div class="w-full md:w-2/3 relative">
                <div class="overflow-hidden rounded-sm shadow-2xl">
                  <img
                    alt="遵义会议会址"
                    class="w-full h-[400px] md:h-[500px] object-cover transition-transform duration-1000 group-hover:scale-105 filter sepia-[0.2]"
                    loading="lazy"
                    decoding="async"
                    width="1280"
                    height="500"
                    :src="themeHistoryUrl"
                  />
                </div>
                <div
                  class="absolute -top-4 -left-4 w-full h-full border-2 border-[#a61f2d]/20 -z-10 hidden md:block transition-all group-hover:-top-6 group-hover:-left-6"
                ></div>
              </div>
              <div class="w-full md:w-1/2 md:-ml-24 mt-8 md:mt-0 relative z-20">
                <div
                  class="bg-white/95 backdrop-blur-sm p-8 md:p-12 shadow-xl border-l-4 border-[#a61f2d]"
                >
                  <div class="flex items-center justify-between mb-6">
                    <span
                      class="text-6xl text-gray-100 font-black/5 absolute -top-8 right-4 select-none"
                      >01</span
                    >
                    <h3 class="text-3xl font-serif font-bold text-gray-800">
                      伟大转折
                    </h3>
                    <span
                      class="px-3 py-1 bg-red-50 text-[#a61f2d] text-xs tracking-wider font-bold uppercase"
                      >History</span
                    >
                  </div>
                  <p class="text-gray-600 leading-relaxed mb-6 text-justify">
                    以遵义会议会址为核心锚点，呈现红色历史的关键节点与叙事线索。
                  </p>
                  <div
                    class="flex items-center text-gray-900 font-bold group-hover:text-[#a61f2d] transition-colors"
                  >
                    <span class="border-b-2 border-current pb-1"
                      >进入历史分区</span
                    >
                    <svg
                      class="w-5 h-5 ml-2"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        d="M14 5l7 7m0 0l-7 7m7-7H3"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                      ></path>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div
            class="relative group mb-32 md:mb-40 cursor-pointer"
            @click="router.push('/highlights')"
          >
            <div class="flex flex-col md:flex-row-reverse items-center">
              <div class="w-full md:w-2/3 relative">
                <div class="overflow-hidden rounded-sm shadow-2xl">
                  <img
                    alt="云海茶园"
                    class="w-full h-[400px] md:h-[500px] object-cover transition-transform duration-1000 group-hover:scale-105"
                    loading="lazy"
                    decoding="async"
                    width="1280"
                    height="500"
                    :src="themeNatureUrl"
                  />
                </div>
                <div
                  class="absolute -bottom-4 -right-4 w-full h-full border-2 border-[#5d7a46]/20 -z-10 hidden md:block transition-all group-hover:-bottom-6 group-hover:-right-6"
                ></div>
              </div>
              <div class="w-full md:w-1/2 md:-mr-24 mt-8 md:mt-0 relative z-20">
                <div
                  class="bg-white/95 backdrop-blur-sm p-8 md:p-12 shadow-xl border-r-4 border-[#5d7a46] text-right"
                >
                  <div
                    class="flex items-center justify-between mb-6 flex-row-reverse"
                  >
                    <span
                      class="text-6xl text-gray-100 font-black/5 absolute -top-8 left-4 select-none"
                      >02</span
                    >
                    <h3 class="text-3xl font-serif font-bold text-gray-800">
                      山水画卷
                    </h3>
                    <span
                      class="px-3 py-1 bg-green-50 text-[#5d7a46] text-xs tracking-wider font-bold uppercase"
                      >Nature</span
                    >
                  </div>
                  <p
                    class="text-gray-600 leading-relaxed mb-6 text-justify"
                    style="direction: rtl"
                  >
                    以山水地貌为线索构建生态景观索引，形成自然资源的系统化呈现。
                  </p>
                  <div
                    class="flex items-center justify-end text-gray-900 font-bold group-hover:text-[#5d7a46] transition-colors ml-auto"
                  >
                    <span class="border-b-2 border-current pb-1"
                      >进入山水分区</span
                    >
                    <svg
                      class="w-5 h-5 ml-2"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        d="M14 5l7 7m0 0l-7 7m7-7H3"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                      ></path>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div
            class="relative group cursor-pointer"
            @click="router.push('/overview')"
          >
            <div class="flex flex-col md:flex-row items-center">
              <div class="w-full md:w-2/3 relative">
                <div class="overflow-hidden rounded-sm shadow-2xl">
                  <img
                    alt="烈士纪念碑"
                    class="w-full h-[400px] md:h-[500px] object-cover transition-transform duration-1000 group-hover:scale-105"
                    loading="lazy"
                    decoding="async"
                    width="1280"
                    height="500"
                    :src="themeSpiritUrl"
                  />
                </div>
                <div
                  class="absolute -top-4 -left-4 w-full h-full border-2 border-[#29312e]/20 -z-10 hidden md:block transition-all group-hover:-top-6 group-hover:-left-6"
                ></div>
              </div>
              <div class="w-full md:w-1/2 md:-ml-24 mt-8 md:mt-0 relative z-20">
                <div
                  class="bg-white/95 backdrop-blur-sm p-8 md:p-12 shadow-xl border-l-4 border-[#29312e]"
                >
                  <div class="flex items-center justify-between mb-6">
                    <span
                      class="text-6xl text-gray-100 font-black/5 absolute -top-8 right-4 select-none"
                      >03</span
                    >
                    <h3 class="text-3xl font-serif font-bold text-gray-800">
                      精神地标
                    </h3>
                    <span
                      class="px-3 py-1 bg-slate-50 text-[#29312e] text-xs tracking-wider font-bold uppercase"
                      >Spirit</span
                    >
                  </div>
                  <p class="text-gray-600 leading-relaxed mb-6 text-justify">
                    以纪念地标为核心构建精神文化谱系，形成可追溯的价值叙事路径。
                  </p>
                  <div
                    class="flex items-center text-gray-900 font-bold group-hover:text-[#29312e] transition-colors"
                  >
                    <span class="border-b-2 border-current pb-1"
                      >进入精神分区</span
                    >
                    <svg
                      class="w-5 h-5 ml-2"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        d="M14 5l7 7m0 0l-7 7m7-7H3"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                      ></path>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<style scoped>
#hero-banner {
  height: 680px;
}

.z-bg-text {
  position: absolute;
  top: 800px;
  left: 0;
  font-size: 200px;
  font-weight: 900;
  color: #f2ebe1;
  opacity: 0.5;
  user-select: none;
  pointer-events: none;
  z-index: 0;
  writing-mode: vertical-rl;
  font-family: "Times New Roman", serif;
}
</style>
