<script setup>
/**
 * 区域表单组件。
 *
 * 用于后台创建与编辑行政区划信息，维护区域简介、
 * 排序权重、地图坐标与封面素材。
 */
import { ref, onMounted, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";
import request from "@/utils/request";
import { ElMessage } from "element-plus";
import ImageUploader from "@/components/ImageUploader.vue";
import {
  Picture,
  ArrowLeft,
  LocationInformation,
  OfficeBuilding,
  RefreshLeft,
  Check,
  Sort,
  MapLocation,
} from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();

const loading = ref(false);
const isEdit = !!route.params.id;
const formRef = ref(null);

const form = reactive({
  name: "",
  type: "",
  alias: "",
  address: "",
  banner_url: "",
  description: "",
  sort_order: 0,
  status: 1,
  longitude: undefined,
  latitude: undefined,
});

const rules = {
  name: [{ required: true, message: "请输入区域名称", trigger: "blur" }],
  type: [{ required: true, message: "请选择行政区划类型", trigger: "change" }],
  address: [
    { required: true, message: "请输入政府驻地或中心地址", trigger: "blur" },
  ],
};

/**
 * 读取区域详情并回填表单。
 * @returns {Promise<void>}
 */
const loadDetail = async () => {
  if (!isEdit) return;
  loading.value = true;
  try {
    const res = await request.get(`/admin/regions/${route.params.id}`);
    if (res.code === 200 && res.data) {
      Object.assign(form, res.data);
    }
  } catch (e) {
    ElMessage.error("加载详情失败");
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

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        if (isEdit) {
          await request.put(`/admin/regions/${route.params.id}`, form);
          ElMessage.success("更新成功");
        } else {
          await request.post("/admin/regions", form);
          ElMessage.success("新增成功");
        }
        router.push("/admin/region");
      } catch (e) {
        ElMessage.error(e.response?.data?.error || "操作失败");
      } finally {
        loading.value = false;
      }
    } else {
      ElMessage.warning("请完善表单必填项");
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

onMounted(loadDetail);
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
              {{ isEdit ? "编辑区域信息" : "新增区域" }}
            </h2>
            <p v-if="isEdit" class="text-xs text-gray-400 mt-1 font-mono">
              ID: {{ route.params.id }}
            </p>
            <p v-else class="text-xs text-gray-400 mt-1">
              配置全域旅游地图的基础行政单元
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
        class="grid grid-cols-1 lg:grid-cols-3 gap-8"
      >
        <div class="lg:col-span-2 space-y-6">
          <div class="bg-white rounded-lg">
            <h3
              class="text-base font-bold text-gray-800 mb-4 border-l-4 border-blue-500 pl-3"
            >
              基本概况
            </h3>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <el-form-item label="区域名称" prop="name">
                <el-input
                  v-model="form.name"
                  placeholder="如：红花岗区"
                  maxlength="20"
                  show-word-limit
                />
              </el-form-item>

              <el-form-item label="行政类型" prop="type">
                <el-select
                  v-model="form.type"
                  class="w-full"
                  placeholder="请选择"
                >
                  <el-option label="市辖区" value="市辖区" />
                  <el-option label="县" value="县" />
                  <el-option label="自治县" value="自治县" />
                  <el-option label="县级市" value="县级市" />
                </el-select>
              </el-form-item>

              <el-form-item label="城市别名/美誉" prop="alias">
                <el-input
                  v-model="form.alias"
                  placeholder="如：中国酒都、吉他之乡"
                />
              </el-form-item>

              <el-form-item label="政府驻地/中心地址" prop="address">
                <el-input v-model="form.address" placeholder="如：中山路1号">
                  <template #prefix
                    ><el-icon><OfficeBuilding /></el-icon
                  ></template>
                </el-input>
              </el-form-item>
            </div>
          </div>

          <div class="bg-white rounded-lg pt-4 border-t border-gray-100">
            <h3
              class="text-base font-bold text-gray-800 mb-4 border-l-4 border-blue-500 pl-3"
            >
              区域详情
            </h3>
            <el-form-item label="区域简介" prop="description">
              <el-input
                v-model="form.description"
                placeholder="请简要介绍该区域的地理位置、历史文化、特色产业及著名景点..."
                rows="6"
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
              <el-icon><Sort /></el-icon>
              <span>显示配置</span>
            </div>

            <el-form-item label="排序权重 (Order)" prop="sort_order">
              <el-input-number
                v-model="form.sort_order"
                :min="0"
                controls-position="right"
                class="w-full"
              />
              <div class="text-xs text-gray-400 mt-1">
                数值越小，在列表中越靠前
              </div>
            </el-form-item>

            <el-form-item label="启用状态" class="mb-0">
              <div class="flex items-center justify-between w-full">
                <span class="text-xs text-gray-500 mr-2">是否在前端展示</span>
                <el-switch
                  v-model="form.status"
                  :active-value="1"
                  :inactive-value="0"
                  inline-prompt
                  active-text="启用"
                  inactive-text="禁用"
                />
              </div>
            </el-form-item>
          </div>

          <div
            class="bg-gray-50 p-6 rounded-xl border border-gray-200 shadow-sm"
          >
            <div class="flex items-center gap-2 mb-4 text-gray-700 font-bold">
              <el-icon><LocationInformation /></el-icon>
              <span>中心坐标 (Map)</span>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <el-form-item
                label="经度 (Lng)"
                prop="longitude"
                class="col-span-2 sm:col-span-1 lg:col-span-2 xl:col-span-1"
              >
                <el-input v-model="form.longitude" placeholder="106.xxxx">
                  <template #prefix>E</template>
                </el-input>
              </el-form-item>
              <el-form-item
                label="纬度 (Lat)"
                prop="latitude"
                class="col-span-2 sm:col-span-1 lg:col-span-2 xl:col-span-1"
              >
                <el-input v-model="form.latitude" placeholder="27.xxxx">
                  <template #prefix>N</template>
                </el-input>
              </el-form-item>
            </div>
            <div class="text-xs text-gray-400 mt-2 flex items-center gap-1">
              <el-icon><MapLocation /></el-icon>
              用于全域地图导航定位
            </div>
          </div>

          <div class="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <div class="flex items-center gap-2 mb-4 text-gray-700 font-bold">
              <el-icon><Picture /></el-icon>
              <span>封面图片</span>
            </div>

            <el-form-item prop="banner_url">
              <ImageUploader
                v-model="form.banner_url"
                scope="region"
                hint="建议使用 16:9 横图，支持 JPG、PNG、WebP，不超过 5MB"
              />
            </el-form-item>
          </div>
        </div>
      </el-form>
    </div>
  </div>
</template>
