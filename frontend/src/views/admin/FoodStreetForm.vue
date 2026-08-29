<script setup>
/**
 * 美食街区表单组件。
 *
 * 用于后台创建与编辑街区资源，维护街区概况、
 * 推荐标签与视觉素材信息。
 */
import { ref, onMounted, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";
import request from "@/utils/request";
import { ElMessage } from "element-plus";
import ImageUploader from "@/components/ImageUploader.vue";
import {
  Picture,
  ArrowLeft,
  Dish,
  Location,
  Shop,
  RefreshLeft,
  Check,
  CollectionTag,
} from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();

const loading = ref(false);
const isEdit = !!route.params.id;
const formRef = ref(null);

const form = reactive({
  name: "",
  alias: "",
  address: "",
  description: "",
  recommend_tags: "",
  image_url: "",
  banner_url: "",
  status: 1,
});

const rules = {
  name: [
    { required: true, message: "请输入街区名称", trigger: "blur" },
    { min: 2, max: 50, message: "长度在 2 到 50 个字符", trigger: "blur" },
  ],
  address: [{ required: true, message: "请输入详细地址", trigger: "blur" }],
};

/**
 * 读取街区详情并回填表单。
 * @returns {Promise<void>}
 */
const loadDetail = async () => {
  if (!isEdit) return;
  loading.value = true;
  try {
    const res = await request.get(`/admin/food-streets/${route.params.id}`);
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
          await request.put(`/admin/food-streets/${route.params.id}`, form);
          ElMessage.success("更新成功");
        } else {
          await request.post("/admin/food-streets", form);
          ElMessage.success("新增成功");
        }
        router.push("/admin/food-street");
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
              {{ isEdit ? "编辑美食街区" : "新增美食街区" }}
            </h2>
            <p v-if="isEdit" class="text-xs text-gray-400 mt-1 font-mono">
              ID: {{ route.params.id }}
            </p>
            <p v-else class="text-xs text-gray-400 mt-1">
              汇聚城市烟火气，录入热门夜市与街区
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
              class="text-base font-bold text-gray-800 mb-4 border-l-4 border-red-500 pl-3"
            >
              街区概况
            </h3>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <el-form-item label="街区名称" prop="name">
                <el-input
                  v-model="form.name"
                  placeholder="如：捞沙巷美食街"
                  maxlength="50"
                  show-word-limit
                >
                  <template #prefix
                    ><el-icon><Shop /></el-icon
                  ></template>
                </el-input>
              </el-form-item>

              <el-form-item label="宣传别名/Slogan" prop="alias">
                <el-input v-model="form.alias" placeholder="如：遵义味道聚集地">
                  <template #prefix
                    ><el-icon><CollectionTag /></el-icon
                  ></template>
                </el-input>
              </el-form-item>

              <el-form-item
                label="详细地址"
                prop="address"
                class="col-span-1 md:col-span-2"
              >
                <el-input
                  v-model="form.address"
                  placeholder="如：红花岗区步行街中段"
                >
                  <template #prefix
                    ><el-icon><Location /></el-icon
                  ></template>
                </el-input>
              </el-form-item>
            </div>
          </div>

          <div class="bg-white rounded-lg pt-4 border-t border-gray-100">
            <h3
              class="text-base font-bold text-gray-800 mb-4 border-l-4 border-red-500 pl-3"
            >
              详细介绍
            </h3>

            <el-form-item label="街区简介" prop="description">
              <el-input
                v-model="form.description"
                placeholder="请介绍街区的历史沿革、特色氛围、主要营业时间等..."
                rows="6"
                type="textarea"
                resize="none"
                maxlength="500"
                show-word-limit
              />
            </el-form-item>

            <el-form-item label="推荐美食标签 (Tags)" prop="recommend_tags">
              <el-input
                v-model="form.recommend_tags"
                placeholder="如：羊肉粉, 恋爱豆腐果, 冰粉 (请用逗号分隔)"
                type="textarea"
                rows="3"
                resize="none"
              >
                <template #prefix
                  ><el-icon><Dish /></el-icon
                ></template>
              </el-input>
              <div class="text-xs text-gray-400 mt-2 flex items-center gap-1">
                <el-icon><Dish /></el-icon>
                <span
                  >用于前端展示关键词标签，建议使用中文或英文逗号分隔。</span
                >
              </div>
            </el-form-item>
          </div>
        </div>

        <div class="lg:col-span-1 space-y-6">
          <div
            class="bg-red-50/50 p-6 rounded-xl border border-red-100 shadow-sm"
          >
            <div class="flex items-center gap-2 mb-4 text-red-800 font-bold">
              <el-icon><Shop /></el-icon>
              <span>运营状态</span>
            </div>

            <el-form-item label="显示状态" class="mb-0">
              <div class="flex items-center justify-between w-full">
                <span class="text-xs text-gray-500 mr-2">控制前端是否可见</span>
                <el-switch
                  v-model="form.status"
                  :active-value="1"
                  :inactive-value="0"
                  inline-prompt
                  active-text="营业"
                  inactive-text="隐藏"
                  style="
                    --el-switch-on-color: #687565;
                    --el-switch-off-color: #a61f2d;
                  "
                />
              </div>
            </el-form-item>
          </div>

          <div class="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <div class="flex items-center gap-2 mb-4 text-gray-700 font-bold">
              <el-icon><Picture /></el-icon>
              <span>视觉素材</span>
            </div>

            <el-form-item label="列表小图" prop="image_url">
              <ImageUploader v-model="form.image_url" scope="food-street" />
            </el-form-item>

            <el-form-item label="详情Banner大图" prop="banner_url">
              <ImageUploader
                v-model="form.banner_url"
                scope="food-street"
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
