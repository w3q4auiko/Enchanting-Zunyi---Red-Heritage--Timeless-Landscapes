<script setup>
/**
 * 美食管理列表组件。
 *
 * 提供美食资源的检索、分页与删除能力，支撑后台餐饮信息治理。
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
  Shop,
  Food,
  Money,
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
 * 拉取美食列表数据。
 * @returns {Promise<void>}
 */
const fetchList = async () => {
  loading.value = true;
  try {
    const res = await request.get("/admin/foods", {
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
    console.error("Fetch food list error:", e);
    ElMessage.error("获取数据失败，请重试");
  } finally {
    loading.value = false;
  }
};

/**
 * 映射美食类别到标签类型。
 * @param {string} cat - 美食类别。
 * @returns {string} 标签类型。
 */
const getCategoryType = (cat) => {
  const map = {
    遵义粉面: "warning",
    街头小吃: "danger",
    地道大菜: "success",
    甜品冷饮: "info",
    名茶佳酿: "primary",
    山珍寻味: "",
    特产手信: "warning",
  };
  return map[cat] || "";
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
 * 删除指定美食记录。
 * @param {number} id - 美食主键。
 * @param {string} name - 美食名称。
 * @returns {void}
 */
const handleDelete = (id, name) => {
  ElMessageBox.confirm(
    `确定要永久删除美食 "${name}" 吗？此操作不可恢复。`,
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
        await request.delete(`/admin/foods/${id}`);
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
 * 跳转到美食编辑页。
 * @param {number} id - 美食主键。
 * @returns {void}
 */
const handleEdit = (id) => {
  router.push(`/admin/food/edit/${id}`);
};

/**
 * 跳转到美食新增页。
 * @returns {void}
 */
const handleAdd = () => {
  router.push("/admin/food/add");
};

onMounted(fetchList);
</script>

<template>
  <div class="admin-page">
    <section class="admin-panel admin-table-panel">
      <div class="admin-toolbar">
        <div class="admin-page-heading">
          <h2>特色美食</h2>
          <p>维护美食资料、推荐店铺与前台展示状态</p>
        </div>
        <div class="admin-toolbar-actions">
          <el-input
            v-model="query.keyword"
            class="w-64"
            clearable
            placeholder="搜索美食名称/店铺"
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
            新增美食
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
              :alt="row.name || '美食封面'"
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

        <el-table-column label="美食概况" min-width="180">
          <template #default="{ row }">
            <div class="flex flex-col gap-1 py-1">
              <span
                class="font-bold text-gray-800 text-base flex items-center gap-2"
              >
                {{ row.name }}
              </span>
              <div class="mt-1">
                <el-tag
                  :type="getCategoryType(row.category)"
                  effect="plain"
                  size="small"
                  round
                >
                  {{ row.category }}
                </el-tag>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="探店信息" min-width="200">
          <template #default="{ row }">
            <div class="space-y-2 text-sm text-gray-600">
              <div class="flex items-center" title="推荐店铺">
                <el-icon class="mr-1.5 text-orange-500"><Shop /></el-icon>
                <span class="font-medium truncate">{{
                  row.recommend_shop || "暂无推荐店铺"
                }}</span>
              </div>
              <div class="flex items-center" title="人均价格">
                <el-icon class="mr-1.5 text-green-600"><Money /></el-icon>
                <span v-if="row.price">{{ row.price }}</span>
                <span v-else class="text-gray-300 text-xs">价格未知</span>
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
              {{ row.status === 1 ? "上架" : "下架" }}
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
  justify-content: center;
}

:deep(.el-table .el-table__cell.is-left .cell) {
  justify-content: flex-start;
}
</style>
