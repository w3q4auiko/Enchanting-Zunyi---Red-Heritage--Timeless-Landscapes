<script setup>
/**
 * 区域管理列表组件。
 *
 * 提供行政区划资源的检索、分页与删除能力，支撑全域数据治理。
 */
import { ref, onMounted, reactive } from "vue";
import { useRouter } from "vue-router";
import request from "@/utils/request";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Plus,
  Search,
  Edit,
  Delete,
  Location,
  Picture,
  OfficeBuilding,
} from "@element-plus/icons-vue";

const router = useRouter();

const list = ref([]);
const loading = ref(false);
const total = ref(0);

const query = reactive({
  page: 1,
  limit: 10,
  keyword: "",
});

/**
 * 拉取区域列表数据。
 * @returns {Promise<void>}
 */
const fetchList = async () => {
  loading.value = true;
  try {
    const res = await request.get("/admin/regions", {
      params: {
        page: query.page,
        limit: query.limit,
        keyword: query.keyword,
      },
    });

    if (res.code === 200) {
      list.value = res.data || [];
      total.value = res.total || 0;
    } else {
      list.value = [];
      total.value = 0;
    }
  } catch (e) {
    console.error("Fetch regions error:", e);
    ElMessage.error("获取数据失败，请检查网络");
  } finally {
    loading.value = false;
  }
};

/**
 * 执行检索并重置到第一页。
 * @returns {void}
 */
const handleSearch = () => {
  query.page = 1;
  fetchList();
};

/**
 * 切换分页页码。
 * @param {number} val - 新页码。
 * @returns {void}
 */
const handleCurrentChange = (val) => {
  query.page = val;
  fetchList();
};

/**
 * 删除指定区域。
 * @param {number} id - 区域主键。
 * @param {string} name - 区域名称。
 * @returns {void}
 */
const handleDelete = (id, name) => {
  ElMessageBox.confirm(
    `确定要永久删除区域 "${name}" 吗？此操作不可恢复。`,
    "高风险操作警告",
    {
      confirmButtonText: "确定删除",
      cancelButtonText: "取消",
      type: "warning",
      draggable: true,
      appendTo: document.body,
    },
  )
    .then(async () => {
      try {
        await request.delete(`/admin/regions/${id}`);
        ElMessage.success("删除成功");

        if (list.value.length === 1 && query.page > 1) {
          query.page--;
        }
        fetchList();
      } catch (e) {
        const msg = e.response?.data?.error || "删除失败";
        ElMessage.error(msg);
      }
    })
    .catch(() => {});
};

/**
 * 跳转到区域编辑页。
 * @param {number} id - 区域主键。
 * @returns {void}
 */
const handleEdit = (id) => {
  router.push(`/admin/region/edit/${id}`);
};

/**
 * 跳转到区域新增页。
 * @returns {void}
 */
const handleAdd = () => {
  router.push("/admin/region/add");
};

onMounted(fetchList);
</script>

<template>
  <div class="admin-page">
    <section class="admin-panel admin-table-panel">
      <div class="admin-toolbar">
        <div class="admin-page-heading">
          <h2>区域内容</h2>
          <p>维护区县概况、地理资料与前台展示状态</p>
        </div>
        <div class="admin-toolbar-actions">
          <el-input
            v-model="query.keyword"
            class="w-64"
            clearable
            placeholder="搜索区域名称"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>

          <el-button type="primary" @click="handleSearch" :icon="Search"
            >查询</el-button
          >
          <el-button type="success" @click="handleAdd" :icon="Plus"
            >新增区域</el-button
          >
        </div>
      </div>

      <el-table
        v-loading="loading"
        :data="list"
        border
        stripe
        class="admin-data-table"
        header-cell-class-name="bg-blue-50 text-gray-700 font-bold"
        highlight-current-row
      >
        <el-table-column
          align="center"
          label="ID"
          prop="id"
          width="80"
          sortable
        />

        <el-table-column align="center" label="封面概览" width="120">
          <template #default="{ row }">
            <el-image
              v-if="row.banner_url"
              :preview-src-list="[row.banner_url]"
              :src="row.banner_url"
              :alt="row.name || '区域封面'"
              lazy
              class="w-20 h-14 rounded border border-gray-200 object-cover shadow-sm cursor-zoom-in"
              fit="cover"
              preview-teleported
              hide-on-click-modal
            >
              <template #error>
                <div
                  class="w-full h-full flex items-center justify-center bg-gray-100 text-gray-400"
                >
                  <el-icon><Picture /></el-icon>
                </div>
              </template>
            </el-image>
            <span v-else class="text-gray-300 text-xs italic">暂无图片</span>
          </template>
        </el-table-column>

        <el-table-column label="行政区域" min-width="160">
          <template #default="{ row }">
            <div class="flex flex-col gap-1 py-1">
              <span class="font-bold text-gray-800 text-base">{{
                row.name
              }}</span>
              <div class="mt-1">
                <el-tag effect="plain" size="small" type="info" round>
                  {{ row.type || "未知类型" }}
                </el-tag>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="详细信息" min-width="220">
          <template #default="{ row }">
            <div class="space-y-2 text-sm">
              <div
                v-if="row.alias"
                class="flex items-center text-blue-600 bg-blue-50 w-fit px-2 py-0.5 rounded"
              >
                <span class="font-semibold text-xs mr-1">别名:</span>
                {{ row.alias }}
              </div>
              <div class="flex items-start text-gray-600">
                <el-icon class="mt-0.5 mr-1 text-gray-400 flex-shrink-0"
                  ><OfficeBuilding
                /></el-icon>
                <span>{{ row.address || "暂无政府驻地信息" }}</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column align="center" label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 1 ? 'success' : 'info'"
              effect="dark"
              size="small"
            >
              {{ row.status === 1 ? "显示" : "隐藏" }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column align="center" fixed="right" label="操作" width="180">
          <template #default="{ row }">
            <el-button
              :icon="Edit"
              link
              type="primary"
              @click="handleEdit(row.id)"
            >
              编辑
            </el-button>
            <el-button
              :icon="Delete"
              link
              type="danger"
              @click="handleDelete(row.id, row.name)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="admin-pagination">
        <el-pagination
          v-model:current-page="query.page"
          v-model:page-size="query.limit"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          background
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchList"
          @current-change="handleCurrentChange"
        />
      </div>
    </section>
  </div>
</template>

<style scoped>
:deep(.el-table .cell) {
  display: flex;
  align-items: center;
}
</style>
