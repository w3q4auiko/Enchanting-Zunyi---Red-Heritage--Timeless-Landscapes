<script setup>
/**
 * @file Overview.vue
 * @description 红色记忆总览页，面向旅游信息系统的“历史叙事入口”场景。
 * 设计意图：以精选卡片与索引矩阵构建红色文化导览的双层结构。
 * 架构视角：视图层仅承担内容编排与交互增强，数据来源保持后端统一。
 */
import { nextTick, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { applyDragScroll, fixUrl } from "@/utils/common.js";
import { getAttractions } from "@/api/tourism.js";
import overviewBannerUrl from "@/assets/images/banners/red-city-context-zine.webp";

const router = useRouter();




const impressionItems = ref([]);

const dbAttractions = ref([]);

const isLoading = ref(true);




const redSiteConfig = [
  {
    category: "重要会议旧址",
    items: [
      { text: "遵义会议会址", sub: "(中央红军指挥中枢)", keyWord: "遵义会议" },
      { text: "苟坝会议旧址", sub: "(军事指挥权完善地)", keyWord: "苟坝" },
      {
        text: "泗渡红军总司令部旧址",
        sub: "(遵义大捷后的战略调整)",
        keyWord: "泗渡",
      },
    ],
  },
  {
    category: "关键战斗与渡口遗址",
    items: [
      { text: "乌江渡口遗址/纪念碑", sub: "(突破天险)", keyWord: "乌江" },
      { text: "桐梓县红军长征遗址", sub: "(娄山关)", keyWord: "娄山关" },
      { text: "老鸦山战斗遗址", sub: "(遵义大捷核心战场)", keyWord: "老鸦山" },
      {
        text: "青杠坡战斗遗址",
        sub: "(一渡赤水前夕的血战)",
        keyWord: "青杠坡",
      },
    ],
  },
  {
    category: "四渡赤水渡口群",
    items: [
      { text: "土城渡口纪念碑", sub: "(一渡赤水)", keyWord: "土城" },
      { text: "二郎滩渡口", sub: "(二渡赤水)", keyWord: "二郎滩" },
      { text: "茅台渡口纪念碑", sub: "(三渡赤水)", keyWord: "茅台" },
      { text: "太平渡长征遗址", sub: "(四渡赤水)", keyWord: "太平渡" },
    ],
  },
  {
    category: "纪念馆与烈士陵园",
    items: [
      {
        text: "四渡赤水纪念馆",
        sub: "(核心专题馆)",
        keyWord: "四渡赤水纪念馆",
      },
      { text: "中国女红军纪念馆", sub: "(全国唯一)", keyWord: "女红军" },
      { text: "遵义红军烈士陵园", sub: "(红军山)", keyWord: "烈士陵园" },
    ],
  },
];




/**
 * 拉取红色文化景点数据并构建首页叙事卡片与索引。
 * @returns {Promise<void>} 数据装载完成后更新加载态。
 */
const fetchAllData = async () => {
  try {
    isLoading.value = true;

    const res = await getAttractions("红色文化");
    const allData = res || [];
    dbAttractions.value = allData;

    
    const whiteList = ["遵义会议会址", "娄山关", "四渡赤水纪念馆"];
    const customTexts = {
      遵义会议会址: {
        title: "转折圣地 · 遵义会议",
        desc: "确立了毛泽东同志在党中央和红军的领导地位。",
      },
      娄山关: {
        title: "雄关大捷 · 娄山关",
        desc: "“雄关漫道真如铁，而今迈步从头越。”",
      },
      四渡赤水纪念馆: {
        title: "神来之笔 · 四渡赤水",
        desc: "运动战艺术的巅峰之作，成功跳出数十万大军重围。",
      },
    };

    const filtered = allData.filter((item) =>
      whiteList.some((k) => item.title.includes(k)),
    );

    impressionItems.value = filtered.map((item) => {
      const matchKey = whiteList.find((k) => item.title.includes(k));
      const custom = customTexts[matchKey];
      return {
        id: item.id,
        title: custom ? custom.title : item.title,
        desc: custom ? custom.desc : item.summary || item.description,
        img:
          fixUrl(item.banner_url) ||
          fixUrl(item.image_url) ||
          "/img/overview_hero.jpg",
        url: `/attraction/scenery/${item.id}`,
      };
    });

    
    nextTick(() => {
      const sliders = document.querySelectorAll(".drag-container");
      sliders.forEach((slider) => applyDragScroll(slider));
    });
  } catch (error) {
    console.error(
      "Infrastructure: Overview telemetry data extraction failed.",
      error,
    );
  } finally {
    isLoading.value = false;
  }
};


/**
 * 根据关键字在缓存数据中定位实体 ID。
 * @param {string} keyWord - 关键字或地名片段。
 * @returns {string|null} 命中的实体 ID，若不存在则返回 null。
 */
const findId = (keyWord) => {
  if (!dbAttractions.value.length) return null;
  const target = dbAttractions.value.find((item) =>
    item.title.includes(keyWord),
  );
  return target ? target.id : null;
};


onMounted(fetchAllData);
</script>

<template>
  <div class="page-wrapper flex flex-col min-h-screen bg-[#f6f0e6]">
    <main class="w-full flex-grow overflow-hidden">
      
      <section
        class="relative h-[500px] w-full overflow-hidden flex items-center justify-center"
      >
        <div
          class="absolute inset-0 bg-cover bg-center transition-transform duration-[2s] hover:scale-105"
          :style="{ backgroundImage: `url(${overviewBannerUrl})` }"
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
            从历史深处，走向烟火街头
          </h1>
          <p
            class="text-xl font-light opacity-90 max-w-1xl mx-auto leading-relaxed"
          >
            以时间与地点为线索，将遵义的红色记忆融入城市当下。在这里，每一次探访都是一场与历史的对话——在日常烟火里触摸红色温度。
          </p>
        </div>
      </section>

      
      <div
        id="content"
        class="max-w-[1400px] mx-auto px-4 md:px-8 py-16 space-y-20 w-full overflow-hidden"
      >
        
        <section class="w-full">
          <div
            class="flex items-center justify-between mb-8 px-2 border-l-4 border-[#a61f2d] pl-4"
          >
            <div>
              <span
                class="text-sm font-bold tracking-widest text-[#a61f2d] uppercase"
                >RED LEGACY</span
              >
              <h2 class="text-2xl md:text-3xl font-black text-gray-800 mt-1">
                红色基因：长征史诗的转折地
              </h2>
            </div>
          </div>

          <div v-if="isLoading" class="relative w-full">
            <div
              class="drag-container flex gap-6 pb-12 pt-4 px-2 no-scrollbar w-full overflow-x-auto"
            >
              <div
                v-for="i in 3"
                :key="`overview-skeleton-${i}`"
                class="epic-card relative min-w-[340px] md:min-w-[420px] h-[320px] shrink-0 overflow-hidden rounded-2xl"
              >
                <div class="skeleton h-full w-full"></div>
                <div class="absolute inset-0 p-8 flex flex-col justify-end gap-3">
                  <div class="skeleton h-3 w-24"></div>
                  <div class="skeleton skeleton-line w-2/3"></div>
                  <div class="skeleton skeleton-line w-5/6"></div>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="relative w-full">
            <div
              class="drag-container flex gap-6 pb-12 pt-4 px-2 no-scrollbar cursor-grab active:cursor-grabbing w-full overflow-x-auto"
            >
              <div
                v-for="(item, index) in impressionItems"
                :key="item.id"
                class="epic-card group relative min-w-[340px] md:min-w-[420px] h-[320px] bg-white shadow-xl cursor-pointer shrink-0 overflow-hidden rounded-2xl transition-all duration-500 hover:-translate-y-2"
                @click="router.push(item.url)"
              >
                
                <img
                  :src="item.img"
                  :alt="item.title"
                  class="absolute inset-0 w-full h-full object-cover transition-transform duration-[800ms] group-hover:scale-110"
                  loading="lazy"
                  decoding="async"
                />
                <div
                  class="absolute inset-0 bg-gradient-to-t from-black/95 via-black/40 to-transparent z-10"
                ></div>
                
                <div
                  class="absolute -top-4 -right-2 text-[8rem] font-black text-white/10 select-none z-0 font-serif italic leading-none"
                >
                  {{ (index + 1).toString().padStart(2, "0") }}
                </div>

                <div
                  class="absolute inset-0 z-20 flex flex-col justify-end p-8"
                >
                  <div
                    class="w-12 h-1 bg-[#a61f2d] mb-4 transition-all duration-300 group-hover:w-24"
                  ></div>
                  <h3
                    class="text-2xl md:text-3xl font-bold text-white mb-3 font-serif"
                  >
                    {{ item.title }}
                  </h3>
                  <p
                    class="text-gray-300 text-sm leading-relaxed max-w-[90%] line-clamp-2"
                  >
                    {{ item.desc }}
                  </p>
                  <div
                    class="mt-6 flex items-center text-xs font-bold text-[#a61f2d] uppercase tracking-widest opacity-0 transform translate-y-4 transition-all duration-300 group-hover:opacity-100 group-hover:translate-y-0"
                  >
                    Explore History <span class="ml-2">→</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <hr class="border-gray-100" />

        
        <section class="pb-12 w-full">
          <div class="text-center mb-16">
            <h2
              class="text-3xl md:text-4xl font-black mb-4 text-[#a61f2d] tracking-tight"
            >
              红色印记索引全览
            </h2>
            <div class="w-24 h-1 bg-[#a61f2d] mx-auto rounded-full"></div>
          </div>

          
          <div
            class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-x-12 gap-y-12"
          >
            <div
              v-for="(group, idx) in redSiteConfig"
              :key="idx"
              class="category-block"
            >
              <h3
                class="text-lg font-bold text-gray-800 mb-6 pb-3 border-b-2 border-gray-100 flex items-center"
              >
                <span class="w-2 h-2 bg-[#a61f2d] rounded-full mr-2"></span>
                {{ group.category }}
              </h3>

              <div class="space-y-4">
                <div v-for="(item, i) in group.items" :key="i">
                  
                  <a
                    v-if="findId(item.keyWord)"
                    class="group flex items-start cursor-pointer hover:translate-x-1 transition-transform"
                    @click="
                      router.push(`/attraction/scenery/${findId(item.keyWord)}`)
                    "
                  >
                    <span
                      class="text-gray-700 group-hover:text-[#a61f2d] transition-colors font-medium"
                    >
                      {{ item.text }}
                      <span
                        v-if="item.sub"
                        class="block text-xs text-gray-400 mt-1 font-normal"
                        >{{ item.sub }}</span
                      ></span
                    ></a
                  >
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

