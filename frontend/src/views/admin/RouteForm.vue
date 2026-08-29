<script setup>
/** 旅游路线新增、编辑与用户投稿审核表单。 */
import { onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { ArrowLeft, Check, Picture } from "@element-plus/icons-vue";

import ImageUploader from "@/components/ImageUploader.vue";
import request from "@/utils/request";

const route = useRoute();
const router = useRouter();
const formRef = ref(null);
const loading = ref(false);
const isEdit = Boolean(route.params.id);
const form = reactive({
  category: "山野徒步",
  title: "",
  difficulty: 1,
  distance_km: 0,
  duration_hours: 0,
  climb_meters: 0,
  route_type: "环线",
  start_point: "",
  address: "",
  description: "",
  tips: "",
  image_url: "",
  banner_url: "",
  latitude: undefined,
  longitude: undefined,
  status: 1,
  submitted_by: null,
});
const rules = {
  title: [{ required: true, message: "请输入路线名称", trigger: "blur" }],
  description: [{ required: true, message: "请填写路线介绍", trigger: "blur" }],
};

const loadDetail = async () => {
  if (!isEdit) return;
  loading.value = true;
  try {
    const result = await request.get(`/admin/routes/${route.params.id}`);
    if (result.data) Object.assign(form, result.data);
  } catch (error) {
    ElMessage.error("加载路线详情失败");
  } finally {
    loading.value = false;
  }
};

const submit = async () => {
  if (!formRef.value) return;
  const valid = await formRef.value.validate().catch(() => false);
  if (!valid) return;
  loading.value = true;
  try {
    if (isEdit) await request.put(`/admin/routes/${route.params.id}`, form);
    else await request.post("/admin/routes", form);
    ElMessage.success(isEdit ? "路线保存成功" : "路线创建成功");
    router.push("/admin/route");
  } catch (error) {
    ElMessage.error(error.response?.data?.error || "保存失败");
  } finally {
    loading.value = false;
  }
};

onMounted(loadDetail);
</script>

<template>
  <div class="admin-page">
    <section class="admin-panel admin-form-panel">
      <div class="admin-form-header">
        <div class="flex items-center gap-4">
          <el-button :icon="ArrowLeft" circle @click="router.back()" />
          <div>
            <h2 class="text-2xl font-bold text-gray-800">
              {{ isEdit ? (form.submitted_by ? "审核路线投稿" : "编辑旅游路线") : "新增旅游路线" }}
            </h2>
            <p class="mt-1 text-xs text-gray-400">完善资料并将状态设为“已发布”即可通过审核</p>
          </div>
        </div>
        <el-button :loading="loading" :icon="Check" type="primary" @click="submit">保存</el-button>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div class="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-x-6">
          <el-form-item label="路线名称" prop="title"><el-input v-model="form.title" maxlength="100" /></el-form-item>
          <el-form-item label="分类"><el-input v-model="form.category" maxlength="50" /></el-form-item>
          <el-form-item label="路线类型">
            <el-select v-model="form.route_type" class="w-full"><el-option label="环线" value="环线" /><el-option label="往返" value="往返" /><el-option label="穿越" value="穿越" /></el-select>
          </el-form-item>
          <el-form-item label="难度（1–5）"><el-input-number v-model="form.difficulty" :min="1" :max="5" class="w-full" /></el-form-item>
          <el-form-item label="距离（km）"><el-input-number v-model="form.distance_km" :min="0" :precision="2" class="w-full" /></el-form-item>
          <el-form-item label="预计时长（小时）"><el-input-number v-model="form.duration_hours" :min="0" :precision="1" class="w-full" /></el-form-item>
          <el-form-item label="累计爬升（米）"><el-input-number v-model="form.climb_meters" :min="0" class="w-full" /></el-form-item>
          <el-form-item label="起点"><el-input v-model="form.start_point" maxlength="255" /></el-form-item>
          <el-form-item label="所在地址" class="md:col-span-2"><el-input v-model="form.address" maxlength="255" /></el-form-item>
          <el-form-item label="路线介绍" prop="description" class="md:col-span-2"><el-input v-model="form.description" type="textarea" :rows="7" /></el-form-item>
          <el-form-item label="安全提示/投稿参数" class="md:col-span-2"><el-input v-model="form.tips" type="textarea" :rows="4" /></el-form-item>
          <el-form-item label="纬度"><el-input v-model="form.latitude" /></el-form-item>
          <el-form-item label="经度"><el-input v-model="form.longitude" /></el-form-item>
        </div>

        <aside class="space-y-6">
          <div class="rounded-xl border border-gray-200 bg-white p-5">
            <div class="mb-4 flex items-center gap-2 font-bold text-gray-700"><el-icon><Picture /></el-icon>视觉素材</div>
            <el-form-item label="列表封面"><ImageUploader v-model="form.image_url" scope="route" /></el-form-item>
            <el-form-item label="详情 Banner"><ImageUploader v-model="form.banner_url" scope="route" compact hint="建议使用 16:9 横图" /></el-form-item>
          </div>
          <div class="rounded-xl border border-gray-200 bg-gray-50 p-5">
            <el-form-item label="发布状态" class="mb-0">
              <el-switch v-model="form.status" :active-value="1" :inactive-value="0" active-text="已发布" inactive-text="待审核/隐藏" />
            </el-form-item>
          </div>
        </aside>
      </el-form>
    </section>
  </div>
</template>
