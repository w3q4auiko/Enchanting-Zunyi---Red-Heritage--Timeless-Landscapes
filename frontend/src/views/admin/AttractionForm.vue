<script setup>
/**
 * 景点表单组件。
 *
 * 用于后台创建与编辑景点资源，承载景点基础信息、服务信息、
 * 坐标与视觉素材的集中维护。
 */
import { ref, onMounted, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import request from "@/utils/request";
import ImageUploader from "@/components/ImageUploader.vue";
import {
  Picture,
  ArrowLeft,
  Location,
  Ticket,
  Timer,
  LocationInformation,
  RefreshLeft,
  Check,
} from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();

const loading = ref(false);
const isEdit = !!route.params.id;
const formRef = ref(null);

const form = reactive({
  title: "",
  category: "自然风光",
  slogan: "",
  address: "",
  description: "",
  ticket_info: "免费",
  opening_hours: "全天",
  tips: "",
  image_url: "",
  banner_url: "",
  longitude: undefined,
  latitude: undefined,
  status: 1,
});

const rules = {
  title: [
    { required: true, message: "请输入景点名称", trigger: "blur" },
    { min: 2, max: 50, message: "长度在 2 到 50 个字符", trigger: "blur" },
  ],
  category: [{ required: true, message: "请选择所属分类", trigger: "change" }],
  address: [{ required: true, message: "请输入详细地址", trigger: "blur" }],
  description: [{ required: true, message: "请输入景点介绍", trigger: "blur" }],
};

/**
 * 读取景点详情并回填表单。
 * @returns {Promise<void>}
 */
const loadDetail = async () => {
  if (!isEdit) return;

  loading.value = true;
  try {
    const res = await request.get(`/admin/attractions/${route.params.id}`);
    if (res.code === 200 && res.data) {
      Object.assign(form, res.data);
    }
  } catch (e) {
    console.error("Failed to load details:", e);
    ElMessage.error("无法加载景点详情，请重试");
  } finally {
    loading.value = false;
  }
};

/**
 * 提交表单并执行新增或更新。
 * @returns {Promise<void>}
 */
const handleSubmit = async () => {
  if (!formRef.value) return;

  await formRef.value.validate(async (valid, fields) => {
    if (valid) {
      loading.value = true;
      try {
        if (isEdit) {
          await request.put(`/admin/attractions/${route.params.id}`, form);
          ElMessage.success("景点信息更新成功");
        } else {
          await request.post("/admin/attractions", form);
          ElMessage.success("新景点发布成功");
        }
        router.push("/admin/attraction");
      } catch (e) {
        ElMessage.error(e.response?.data?.error || "操作失败，请检查网络");
      } finally {
        loading.value = false;
      }
    } else {
      ElMessage.warning("请检查表单中标红的必填项");
      return false;
    }
  });
};

/**
 * 重置表单数据。
 * @returns {void}
 */
const handleReset = () => {
  if (!formRef.value) return;
  formRef.value.resetFields();
};

onMounted(() => {
  loadDetail();
});
</script>

<template>
  <div class="admin-page">
    <div
      class="admin-panel admin-form-panel"
    >
      <div
        class="admin-form-header"
      >
        <div class="flex items-center gap-4">
          <el-button
            :icon="ArrowLeft"
            circle
            @click="$router.back()"
            class="shadow-sm"
          />
          <div>
            <h2 class="text-2xl font-bold text-gray-800 tracking-tight">
              {{ isEdit ? "编辑景点信息" : "发布新景点" }}
            </h2>
            <p v-if="isEdit" class="text-xs text-gray-400 mt-1 font-mono">
              UUID: {{ route.params.id }}
            </p>
            <p v-else class="text-xs text-gray-400 mt-1">
              填写以下信息以创建一个新的旅游景点条目
            </p>
          </div>
        </div>
        <div class="flex gap-3">
          <el-button :icon="RefreshLeft" @click="handleReset">重置</el-button>
          <el-button
            :loading="loading"
            :icon="Check"
            type="primary"
            class="px-6"
            @click="handleSubmit"
          >
            {{ isEdit ? "保存更改" : "立即发布" }}
          </el-button>
        </div>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        size="large"
        class="grid grid-cols-1 lg:grid-cols-3 gap-10"
      >
        <div class="lg:col-span-2 space-y-6">
          <div class="bg-white rounded-lg">
            <h3
              class="text-base font-bold text-gray-800 mb-4 border-l-4 border-blue-500 pl-3"
            >
              基础概况
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <el-form-item
                label="景点名称"
                prop="title"
                class="col-span-2 md:col-span-1"
              >
                <el-input
                  v-model="form.title"
                  placeholder="例如：遵义会议会址"
                  maxlength="50"
                  show-word-limit
                />
              </el-form-item>

              <el-form-item
                label="所属分类"
                prop="category"
                class="col-span-2 md:col-span-1"
              >
                <el-select
                  v-model="form.category"
                  class="w-full"
                  placeholder="请选择分类"
                >
                  <el-option label="自然风光" value="自然风光" />
                  <el-option label="红色文化" value="红色文化" />
                  <el-option label="历史古迹" value="历史古迹" />
                  <el-option label="休闲度假" value="休闲度假" />
                </el-select>
              </el-form-item>

              <el-form-item
                label="宣传标语 (Slogan)"
                prop="slogan"
                class="col-span-2"
              >
                <el-input
                  v-model="form.slogan"
                  placeholder="一句话描述景点的特色，例如：转折之城，会议之都"
                />
              </el-form-item>

              <el-form-item label="地理位置" prop="address" class="col-span-2">
                <el-input
                  v-model="form.address"
                  placeholder="请输入详细的地理位置"
                >
                  <template #prefix>
                    <el-icon class="text-gray-400"><Location /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
            </div>
          </div>

          <div class="bg-white rounded-lg">
            <h3
              class="text-base font-bold text-gray-800 mb-4 border-l-4 border-blue-500 pl-3"
            >
              详细内容
            </h3>
            <el-form-item label="景点介绍" prop="description">
              <el-input
                v-model="form.description"
                placeholder="请详细介绍景点的历史背景、游玩亮点、文化内涵等..."
                rows="8"
                type="textarea"
                resize="none"
              />
            </el-form-item>

            <el-form-item label="游玩贴士 (Tips)" prop="tips">
              <el-input
                v-model="form.tips"
                placeholder="建议游玩时长、最佳季节、注意事项等"
                rows="3"
                type="textarea"
                resize="none"
              />
            </el-form-item>
          </div>
        </div>

        <div class="lg:col-span-1 space-y-6">
          <div
            class="bg-blue-50/50 p-6 rounded-xl border border-blue-100 shadow-sm"
          >
            <div class="flex items-center gap-2 mb-4 text-blue-800 font-bold">
              <el-icon><Ticket /></el-icon>
              <span>服务信息</span>
            </div>

            <el-form-item label="门票信息" prop="ticket_info">
              <el-input
                v-model="form.ticket_info"
                placeholder="如：免费 / 80元"
              >
                <template #suffix>RMB</template>
              </el-input>
            </el-form-item>

            <el-form-item label="开放时间" prop="opening_hours">
              <el-input
                v-model="form.opening_hours"
                placeholder="如：08:30 - 17:00"
              >
                <template #prefix
                  ><el-icon><Timer /></el-icon
                ></template>
              </el-input>
            </el-form-item>

            <el-form-item label="当前状态" class="mb-0">
              <div class="flex items-center justify-between w-full">
                <span class="text-xs text-gray-500 mr-2">控制前端是否可见</span>
                <el-switch
                  v-model="form.status"
                  :active-value="1"
                  :inactive-value="0"
                  inline-prompt
                  active-text="上架"
                  inactive-text="下架"
                  style="
                    --el-switch-on-color: #687565;
                    --el-switch-off-color: #a61f2d;
                  "
                />
              </div>
            </el-form-item>
          </div>

          <div
            class="bg-gray-50 p-6 rounded-xl border border-gray-200 shadow-sm"
          >
            <div class="flex items-center gap-2 mb-4 text-gray-700 font-bold">
              <el-icon><LocationInformation /></el-icon>
              <span>坐标定位 (WGS84)</span>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <el-form-item
                label="经度 (Lng)"
                prop="longitude"
                class="col-span-2 sm:col-span-1 lg:col-span-2 xl:col-span-1"
              >
                <el-input-number
                  v-model="form.longitude"
                  :precision="6"
                  :step="0.000001"
                  controls-position="right"
                  class="w-full"
                  placeholder="106.xxxxxx"
                />
              </el-form-item>
              <el-form-item
                label="纬度 (Lat)"
                prop="latitude"
                class="col-span-2 sm:col-span-1 lg:col-span-2 xl:col-span-1"
              >
                <el-input-number
                  v-model="form.latitude"
                  :precision="6"
                  :step="0.000001"
                  controls-position="right"
                  class="w-full"
                  placeholder="27.xxxxxx"
                />
              </el-form-item>
            </div>
            <p class="text-xs text-gray-400 mt-2 leading-relaxed">
              * 用于地图打点，建议通过高德地图拾取坐标系统获取精确数值。
            </p>
          </div>

          <div class="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <div class="flex items-center gap-2 mb-4 text-gray-700 font-bold">
              <el-icon><Picture /></el-icon>
              <span>视觉素材</span>
            </div>

            <el-form-item label="列表封面 (Card Image)" prop="image_url">
              <ImageUploader v-model="form.image_url" scope="attraction" />
            </el-form-item>

            <el-form-item label="顶部横幅 (Hero Banner)" prop="banner_url">
              <ImageUploader
                v-model="form.banner_url"
                scope="attraction"
                compact
                hint="建议使用 16:9 横图，支持 JPG、PNG、WebP，不超过 5MB"
              />
            </el-form-item>
          </div>
        </div>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
:deep(.el-input-number .el-input__inner) {
  text-align: left;
}
</style>
