<script setup>
/**
 * 美食街区管理列表组件。
 *
 * 提供美食街区资源的检索、分页与删除能力，支撑街区内容治理。
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
  Picture,
  Location,
  ForkSpoon,
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
 * 拉取街区列表数据。
 * @returns {Promise<void>}
 */
const fetchList = async () => {
  loading.value = true;
  try {
    const res = await request.get("/admin/food-streets", {
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
    ElMessage.error("获取数据失败");
  } finally {
    loading.value = false;
  }
};

/**
 * 解析推荐标签字段。
 * @param {string} tags - 逗号分隔的标签字符串。
 * @returns {string[]} 标签数组。
 */
const splitTags = (tags) => {
  if (!tags || typeof tags !== "string") return [];
  return tags
    .replace(/，/g, ",")
    .split(",")
    .map((t) => t.trim())
    .filter((t) => t.length > 0);
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
 * 删除指定街区。
 * @param {number} id - 街区主键。
 * @param {string} name - 街区名称。
 * @returns {void}
 */
const handleDelete = (id, name) => {
  ElMessageBox.confirm(
    `确定要永久删除街区 "${name}" 吗？此操作不可恢复。`,
    "删除确认",
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
        await request.delete(`/admin/food-streets/${id}`);
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
 * 跳转到街区编辑页。
 * @param {number} id - 街区主键。
 * @returns {void}
 */
const handleEdit = (id) => {
  router.push(`/admin/food-street/edit/${id}`);
};

/**
 * 跳转到街区新增页。
 * @returns {void}
 */
const handleAdd = () => {
  router.push("/admin/food-street/add");
};

onMounted(fetchList);
</script>

<template>
  <div class="admin-page">
    <section class="admin-panel admin-table-panel">
      <div class="admin-toolbar">
        <div class="admin-page-heading">
          <h2>美食街区</h2>
          <p>维护街区资料、推荐标签与前台展示状态</p>
        </div>
        <div class="admin-toolbar-actions">
          <el-input
            v-model="query.keyword"
            class="w-64"
            clearable
            placeholder="搜索街区名称"
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
          <el-button
            type="success"
            @click="handleAdd"
            :icon="Plus"
            color="#b77b3b"
            style="color: white"
          >
            新增街区
          </el-button>
        </div>
      </div>

      <el-table
        v-loading="loading"
        :data="list"
        border
        stripe
        class="admin-data-table"
        header-cell-class-name="bg-orange-50 text-gray-700 font-bold"
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
              :alt="row.name || '街区封面'"
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

        <el-table-column label="街区名称" min-width="180">
          <template #default="{ row }">
            <div class="flex flex-col gap-1 py-1">
              <span class="font-bold text-gray-800 text-base">{{
                row.name
              }}</span>
              <span
                v-if="row.alias"
                class="text-xs text-orange-500 font-medium bg-orange-50 px-2 py-0.5 rounded w-fit"
              >
                {{ row.alias }}
              </span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="推荐美食标签" min-width="220">
          <template #default="{ row }">
            <div class="flex flex-wrap gap-1.5">
              <el-tag
                v-for="(tag, index) in splitTags(row.recommend_tags)"
                :key="index"
                effect="light"
                size="small"
                type="warning"
                round
              >
                {{ tag }}
              </el-tag>
              <span v-if="!row.recommend_tags" class="text-gray-300 text-xs"
                >暂无标签</span
              >
            </div>
          </template>
        </el-table-column>

        <el-table-column label="详细地址" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="flex items-start text-sm text-gray-600">
              <el-icon class="mt-0.5 mr-1 text-gray-400 flex-shrink-0"
                ><Location
              /></el-icon>
              <span>{{ row.address || "暂无地址信息" }}</span>
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
