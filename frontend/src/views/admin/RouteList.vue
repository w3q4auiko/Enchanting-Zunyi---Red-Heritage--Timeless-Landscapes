<script setup>
/** 旅游路线管理列表，同时承接用户路线投稿审核。 */
import { onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { Delete, Edit, Plus, Search } from "@element-plus/icons-vue";

import request from "@/utils/request";

const router = useRouter();
const rows = ref([]);
const loading = ref(false);
const total = ref(0);
const query = reactive({ page: 1, limit: 10, keyword: "" });

const fetchRows = async () => {
  loading.value = true;
  try {
    const result = await request.get("/admin/routes", { params: query });
    rows.value = result.data || [];
    total.value = result.total || 0;
  } catch (error) {
    console.error("Fetch routes failed:", error);
    ElMessage.error("获取路线数据失败");
  } finally {
    loading.value = false;
  }
};

const search = () => {
  query.page = 1;
  fetchRows();
};

const remove = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除路线“${row.title}”吗？`, "删除确认", {
      type: "warning",
      confirmButtonText: "确定删除",
      cancelButtonText: "取消",
    });
    await request.delete(`/admin/routes/${row.id}`);
    ElMessage.success("删除成功");
    if (rows.value.length === 1 && query.page > 1) query.page -= 1;
    fetchRows();
  } catch (error) {
    if (error !== "cancel" && error !== "close") {
      ElMessage.error(error.response?.data?.error || "删除失败");
    }
  }
};

onMounted(fetchRows);
</script>

<template>
  <div class="admin-page">
    <section class="admin-panel admin-table-panel">
      <div class="admin-toolbar">
        <div class="admin-page-heading">
          <h2>旅游路线</h2>
          <p>维护路线参数，审核用户提交的户外路线</p>
        </div>
        <div class="admin-toolbar-actions">
          <el-input
            v-model="query.keyword"
            clearable
            class="w-64"
            placeholder="搜索路线名称"
            @clear="search"
            @keyup.enter="search"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-button :icon="Search" type="primary" @click="search">查询</el-button>
          <el-button :icon="Plus" type="success" @click="router.push('/admin/route/add')">
            新增路线
          </el-button>
        </div>
      </div>

      <el-table v-loading="loading" :data="rows" border stripe class="admin-data-table">
        <el-table-column prop="id" label="ID" width="74" align="center" />
        <el-table-column label="路线信息" min-width="230">
          <template #default="{ row }">
            <div class="font-bold text-gray-800">{{ row.title }}</div>
            <div class="mt-1 flex gap-2">
              <el-tag size="small" effect="plain">{{ row.category || "未分类" }}</el-tag>
              <el-tag v-if="row.submitted_by" size="small" type="warning">用户投稿</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="路线参数" min-width="220">
          <template #default="{ row }">
            <div class="text-sm text-gray-600">
              {{ row.distance_km || 0 }} km · {{ row.duration_hours || 0 }} h ·
              难度 {{ row.difficulty || 1 }}
            </div>
            <div class="mt-1 text-xs text-gray-400">
              {{ row.start_point || row.address || "未填写起点" }}
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'warning'">
              {{ row.status === 1 ? "已发布" : row.submitted_by ? "待审核" : "已隐藏" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="170" fixed="right" align="center">
          <template #default="{ row }">
            <el-button link type="primary" :icon="Edit" @click="router.push(`/admin/route/edit/${row.id}`)">
              编辑/审核
            </el-button>
            <el-button link type="danger" :icon="Delete" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="admin-pagination">
        <el-pagination
          v-model:current-page="query.page"
          v-model:page-size="query.limit"
          :total="total"
          :page-sizes="[10, 20, 50]"
          background
          layout="total, sizes, prev, pager, next"
          @size-change="fetchRows"
          @current-change="fetchRows"
        />
      </div>
    </section>
  </div>
</template>
