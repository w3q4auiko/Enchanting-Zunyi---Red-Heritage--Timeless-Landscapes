<script setup>
/**
 * 用户管理列表组件。
 *
 * 提供后台用户检索、分页与注销能力，维护账号安全边界。
 */
import { ref, onMounted, reactive } from "vue";
import request from "@/utils/request";
import { getUserInfo } from "@/utils/session";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Search,
  Delete,
  UserFilled,
  Refresh,
  Lock,
} from "@element-plus/icons-vue";

const list = ref([]);
const loading = ref(false);
const total = ref(0);
const adminCount = ref(0);
const currentAdminId = Number(getUserInfo()?.id);

const query = reactive({
  page: 1,
  limit: 10,
  keyword: "",
  accountType: "all",
});

/**
 * 拉取用户列表数据。
 * @returns {Promise<void>}
 */
const fetchList = async () => {
  loading.value = true;
  try {
    const res = await request.get("/admin/users", {
      params: {
        page: query.page,
        limit: query.limit,
        keyword: query.keyword,
        account_type: query.accountType,
      },
    });

    if (res.code === 200) {
      if (Array.isArray(res.data)) {
        list.value = res.data;
        total.value = res.total || res.data.length;
      } else {
        list.value = res.data?.list || [];
        total.value = res.data?.total || 0;
      }
      adminCount.value = Number(res.admin_count || 0);
    }
  } catch (e) {
    console.error("Fetch users error:", e);
    ElMessage.error("获取用户数据失败");
  } finally {
    loading.value = false;
  }
};

/**
 * 格式化注册时间。
 * @param {string} timeStr - ISO 时间字符串。
 * @returns {string} 可读时间文本。
 */
const formatTime = (timeStr) => {
  if (!timeStr) return "-";
  return timeStr.replace("T", " ").substring(0, 16);
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
 * 切换分页大小并回到第一页，避免页码超出新分页范围。
 * @param {number} val - 新分页大小。
 * @returns {void}
 */
const handleSizeChange = (val) => {
  query.limit = val;
  query.page = 1;
  fetchList();
};

/**
 * 注销指定用户。
 * @param {object} row - 用户信息对象。
 * @returns {void}
 */
const handleDelete = (row) => {
  const isCurrentAdmin =
    row.account_type === "admin" && row.id === currentAdminId;
  const isLastAdmin = row.account_type === "admin" && adminCount.value <= 1;
  if (isCurrentAdmin || isLastAdmin) {
    ElMessage.warning("当前账号或最后一个管理员不可删除");
    return;
  }

  ElMessageBox.confirm(
    `确定要注销用户 "${row.username}" 吗？此操作不可恢复。`,
    "高风险操作警告",
    {
      confirmButtonText: "确认注销",
      cancelButtonText: "取消",
      type: "warning",
      icon: UserFilled,
      appendTo: document.body,
    },
  )
    .then(async () => {
      try {
        await request.delete(`/admin/users/${row.account_type}/${row.id}`, {
          skipGlobalHandler: true,
        });
        ElMessage.success("用户已成功注销");
        fetchList();
      } catch (e) {
        ElMessage.error(e.response?.data?.error || "删除操作失败");
      }
    })
    .catch(() => {});
};

onMounted(fetchList);
</script>

<template>
  <div class="admin-page">
    <section class="admin-panel admin-table-panel">
      <div class="admin-toolbar">
        <div class="admin-page-heading">
          <h2>用户账号</h2>
          <p>统一管理管理员与普通用户账号，查看角色权限和注册时间</p>
        </div>
        <div class="admin-toolbar-actions">
          <el-select
            v-model="query.accountType"
            class="w-36"
            aria-label="账号类型"
            @change="handleSearch"
          >
            <el-option label="全部账号" value="all" />
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="public" />
          </el-select>
          <el-input
            v-model="query.keyword"
            class="w-64"
            clearable
            placeholder="搜索账号/昵称"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>

          <el-button
            type="primary"
            @click="handleSearch"
            :icon="Search"
            color="#9333ea"
            style="color: white"
          >
            查询
          </el-button>
          <el-button
            :icon="Refresh"
            circle
            @click="fetchList"
            title="刷新列表"
          />
        </div>
      </div>

      <el-table
        v-loading="loading"
        :data="list"
        border
        stripe
        class="admin-data-table"
        header-cell-class-name="bg-purple-50 text-gray-700 font-bold"
      >
        <el-table-column align="center" label="ID" prop="id" width="80" />

        <el-table-column label="用户概况" min-width="180">
          <template #default="{ row }">
            <div class="flex items-center gap-3">
              <el-avatar
                :size="36"
                class="bg-purple-100 text-purple-600 font-bold"
              >
                {{
                  (row.nickname || row.username || "U").charAt(0).toUpperCase()
                }}
              </el-avatar>
              <div class="flex flex-col">
                <span class="font-bold text-gray-800 text-sm">{{
                  row.username
                }}</span>
                <span class="text-xs text-gray-500">{{
                  row.nickname || "暂无昵称"
                }}</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column
          align="center"
          label="角色权限"
          prop="role"
          width="120"
        >
          <template #default="{ row }">
            <el-tag
              v-if="row.role === 'admin'"
              type="danger"
              effect="dark"
              size="small"
              round
            >
              管理员
            </el-tag>
            <el-tag v-else type="info" effect="plain" size="small" round>
              普通用户
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column
          label="注册时间"
          prop="create_time"
          width="180"
          align="center"
        >
          <template #default="{ row }">
            <span class="text-gray-500 text-sm font-mono">
              {{ formatTime(row.create_time) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column fixed="right" label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-tooltip
              v-if="
                row.account_type === 'admin' &&
                (row.id === currentAdminId || adminCount <= 1)
              "
              :content="
                row.id === currentAdminId
                  ? '当前登录账号不可注销'
                  : '最后一个管理员不可注销'
              "
              placement="top"
            >
              <el-button link type="info" disabled :icon="Lock">注销</el-button>
            </el-tooltip>

            <el-button
              v-else
              link
              type="danger"
              :icon="Delete"
              @click="handleDelete(row)"
            >
              注销
            </el-button>
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
          @size-change="handleSizeChange"
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
:deep(.el-table .el-table__cell.is-center .cell) {
  justify-content: center;
}
</style>
