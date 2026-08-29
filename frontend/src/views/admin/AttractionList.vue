<script setup>
/**
 * 景点管理列表组件。
 *
 * 提供景点资源的检索、分页与删除能力，支撑后台内容治理流程。
 */
import { ref, onMounted, reactive } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import request from "@/utils/request";
import {
  Plus,
  Search,
  Edit,
  Delete,
  Picture,
  Location,
  Ticket,
  Timer,
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
 * 拉取景点列表数据。
 * @returns {Promise<void>}
 */
const fetchList = async () => {
  loading.value = true;
  try {
    const res = await request.get("/admin/attractions", {
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
    console.error("Fetch list error:", e);
    ElMessage.error("获取数据失败，请检查网络");
  } finally {
    loading.value = false;
  }
};

/**
 * 映射景点类别到标签类型。
 * @param {string} cat - 景点类别。
 * @returns {string} 标签类型。
 */
const getCategoryType = (cat) => {
  const map = {
    自然风光: "success",
    红色文化: "danger",
    历史古迹: "warning",
    休闲度假: "primary",
  };
  return map[cat] || "info";
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
 * 删除指定景点。
 * @param {number} id - 景点主键。
 * @param {string} title - 景点标题。
 * @returns {void}
 */
const handleDelete = (id, title) => {
  ElMessageBox.confirm(
    `确定要永久删除景点 "${title}" 吗？此操作不可恢复。`,
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
        await request.delete(`/admin/attractions/${id}`);
        ElMessage.success("删除成功");

        if (list.value.length === 1 && query.page > 1) {
          query.page--;
        }
        fetchList();
      } catch (e) {
        ElMessage.error("删除失败");
      }
    })
    .catch(() => {});
};

/**
 * 跳转到景点编辑页。
 * @param {number} id - 景点主键。
 * @returns {void}
 */
const handleEdit = (id) => {
  router.push(`/admin/attraction/edit/${id}`);
};

/**
 * 跳转到景点新增页。
 * @returns {void}
 */
const handleAdd = () => {
  router.push("/admin/attraction/add");
};

onMounted(() => {
  fetchList();
});
</script>

<template>
  <div class="admin-page">
    <section class="admin-panel admin-table-panel">
      <div class="admin-toolbar">
        <div class="admin-page-heading">
          <h2>景点内容</h2>
          <p>维护景点资料、开放服务与前台展示状态</p>
        </div>
        <div class="admin-toolbar-actions">
          <el-input
            v-model="query.keyword"
            class="w-64"
            clearable
            placeholder="搜索景点名称/ID"
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
            >新增景点</el-button
          >
        </div>
      </div>

      <el-table
        v-loading="loading"
        :data="list"
        border
        stripe
        class="admin-data-table"
        header-cell-class-name="bg-gray-50 text-gray-700 font-bold"
        highlight-current-row
      >
        <el-table-column
          align="center"
          label="ID"
          prop="id"
          width="80"
          sortable
        />

        <el-table-column align="center" label="封面预览" width="120">
          <template #default="{ row }">
            <el-image
              v-if="row.image_url"
              :preview-src-list="[row.image_url]"
              :src="row.image_url"
              :alt="row.title || '景点封面'"
              lazy
              class="w-20 h-14 rounded border border-gray-200 object-cover cursor-zoom-in shadow-sm"
              fit="cover"
              preview-teleported
              hide-on-click-modal
            >
              <template #error>
                <div
                  class="w-full h-full flex items-center justify-center bg-gray-100 text-gray-400 text-xs"
                >
                  <el-icon size="16"><Picture /></el-icon>
                </div>
              </template>
            </el-image>
            <span v-else class="text-gray-300 text-xs italic">暂无图片</span>
          </template>
        </el-table-column>

        <el-table-column label="景点概况" min-width="200">
          <template #default="{ row }">
            <div class="flex flex-col gap-1 py-1">
              <span class="font-bold text-gray-800 text-base leading-tight">{{
                row.title
              }}</span>
              <div class="flex flex-wrap gap-2 mt-1">
                <el-tag
                  :type="getCategoryType(row.category)"
                  effect="plain"
                  size="small"
                  round
                >
                  {{ row.category }}
                </el-tag>
                <el-tag
                  v-if="row.status === 1"
                  type="success"
                  size="small"
                  effect="dark"
                  >已上架</el-tag
                >
                <el-tag v-else type="info" size="small" effect="dark"
                  >已下架</el-tag
                >
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="服务信息" width="220">
          <template #default="{ row }">
            <div class="space-y-2 text-xs text-gray-600">
              <div class="flex items-center" title="门票价格">
                <el-icon class="mr-1.5 text-green-600"><Ticket /></el-icon>
                <span class="font-medium">{{ row.ticket_info || "免费" }}</span>
              </div>
              <div class="flex items-center" title="开放时间">
                <el-icon class="mr-1.5 text-blue-600"><Timer /></el-icon>
                <span>{{ row.opening_hours || "全天开放" }}</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="地理位置" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="flex items-start text-sm text-gray-600">
              <el-icon class="mt-0.5 mr-1 text-gray-400 flex-shrink-0"
                ><Location
              /></el-icon>
              <span>{{ row.address || "暂无详细地址信息" }}</span>
            </div>
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
              @click="handleDelete(row.id, row.title)"
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
