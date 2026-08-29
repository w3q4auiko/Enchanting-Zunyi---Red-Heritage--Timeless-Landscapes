<script setup>
/**
 * 美食表单组件。
 *
 * 用于后台创建与编辑美食资源，维护美食介绍、分类、
 * 推荐店铺与视觉素材等关键信息。
 */
import { ref, onMounted, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import request from "@/utils/request";
import ImageUploader from "@/components/ImageUploader.vue";
import {
  Picture,
  ArrowLeft,
  Shop,
  Money,
  Bowl,
  RefreshLeft,
  Check,
  LocationInformation,
} from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();

const loading = ref(false);
const isEdit = !!route.params.id;
const formRef = ref(null);

const form = reactive({
  category: "遵义粉面",
  name: "",
  slogan: "",
  recommend_shop: "",
  description: "",
  image_url: "",
  banner_url: "",
  address: "",
  price: "",
  tips: "",
  status: 1,
});

const rules = {
  name: [
    { required: true, message: "请输入美食名称", trigger: "blur" },
    { min: 2, max: 30, message: "长度在 2 到 30 个字符", trigger: "blur" },
  ],
  category: [{ required: true, message: "请选择美食分类", trigger: "change" }],
  price: [{ required: true, message: "请输入人均价格", trigger: "blur" }],
};

/**
 * 读取美食详情并回填表单。
 * @returns {Promise<void>}
 */
const loadDetail = async () => {
  if (!isEdit) return;
  loading.value = true;
  try {
    const res = await request.get(`/admin/foods/${route.params.id}`);
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
          await request.put(`/admin/foods/${route.params.id}`, form);
          ElMessage.success("更新成功");
        } else {
          await request.post("/admin/foods", form);
          ElMessage.success("发布成功");
        }
        router.push("/admin/food");
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
              {{ isEdit ? "编辑美食信息" : "发布新美食" }}
            </h2>
            <p v-if="isEdit" class="text-xs text-gray-400 mt-1 font-mono">
              ID: {{ route.params.id }}
            </p>
            <p v-else class="text-xs text-gray-400 mt-1">
              录入遵义特色地道风味
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
              class="text-base font-bold text-gray-800 mb-4 border-l-4 border-orange-500 pl-3"
            >
              美食概况
            </h3>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <el-form-item label="美食名称" prop="name">
                <el-input
                  v-model="form.name"
                  placeholder="如：遵义羊肉粉"
                  maxlength="30"
                  show-word-limit
                >
                  <template #prefix
                    ><el-icon><Bowl /></el-icon
                  ></template>
                </el-input>
              </el-form-item>

              <el-form-item label="人均价格" prop="price">
                <el-input v-model="form.price" placeholder="如：12-15元">
                  <template #prefix
                    ><el-icon><Money /></el-icon
                  ></template>
                </el-input>
              </el-form-item>
            </div>

            <el-form-item label="美食标语 (Slogan)" prop="slogan" class="mt-4">
              <el-input
                v-model="form.slogan"
                placeholder="如：酸辣鲜香，一口入魂的黔北地道滋味。"
                maxlength="50"
                show-word-limit
              />
            </el-form-item>

            <el-form-item label="美食简介" prop="description" class="mt-4">
              <el-input
                v-model="form.description"
                placeholder="请描述美食的历史渊源、制作工艺、口感特色等..."
                rows="6"
                type="textarea"
                resize="none"
              />
            </el-form-item>

            <el-form-item label="赏味贴士 (Tips)" prop="tips">
              <el-input
                v-model="form.tips"
                placeholder="例如：建议搭配大蒜、多放糊辣椒，或者最佳品尝时间..."
                rows="3"
                type="textarea"
                resize="none"
              />
            </el-form-item>
          </div>

          <div class="bg-white rounded-lg pt-4 border-t border-gray-100">
            <h3
              class="text-base font-bold text-gray-800 mb-4 border-l-4 border-orange-500 pl-3"
            >
              探店指南
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <el-form-item label="推荐店铺" prop="recommend_shop">
                <el-input
                  v-model="form.recommend_shop"
                  placeholder="如：刘二妈米皮"
                >
                  <template #prefix
                    ><el-icon><Shop /></el-icon
                  ></template>
                </el-input>
              </el-form-item>

              <el-form-item label="分布区域/地址" prop="address">
                <el-input
                  v-model="form.address"
                  placeholder="如：红花岗区老城周边"
                >
                  <template #prefix
                    ><el-icon><LocationInformation /></el-icon
                  ></template>
                </el-input>
              </el-form-item>
            </div>
          </div>
        </div>

        <div class="lg:col-span-1 space-y-6">
          <div
            class="bg-orange-50/50 p-6 rounded-xl border border-orange-100 shadow-sm"
          >
            <div class="flex items-center gap-2 mb-4 text-orange-800 font-bold">
              <el-icon><Shop /></el-icon>
              <span>分类与状态</span>
            </div>

            <el-form-item label="所属分类" prop="category">
              <el-select
                v-model="form.category"
                class="w-full"
                placeholder="请选择"
              >
                <el-option label="遵义粉面" value="遵义粉面" />
                <el-option label="街头小吃" value="街头小吃" />
                <el-option label="地道大菜" value="地道大菜" />
                <el-option label="甜品冷饮" value="甜品冷饮" />
                <el-option label="名茶佳酿" value="名茶佳酿" />
                <el-option label="山珍寻味" value="山珍寻味" />
                <el-option label="特产手信" value="特产手信" />
              </el-select>
            </el-form-item>

            <el-form-item label="发布状态" class="mb-0">
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

          <div class="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <div class="flex items-center gap-2 mb-4 text-gray-700 font-bold">
              <el-icon><Picture /></el-icon>
              <span>视觉素材</span>
            </div>

            <el-form-item label="列表小图" prop="image_url">
              <ImageUploader v-model="form.image_url" scope="food" />
            </el-form-item>

            <el-form-item label="详情Banner大图" prop="banner_url">
              <ImageUploader
                v-model="form.banner_url"
                scope="food"
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
