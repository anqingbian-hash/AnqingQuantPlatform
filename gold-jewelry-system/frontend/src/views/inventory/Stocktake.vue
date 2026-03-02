<template>
  <div class="stocktake-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>库存盘点</span>
          <el-space>
            <el-button type="primary" @click="handleCreate">
              <el-icon><Plus /></el-icon>
              新建盘点
            </el-button>
            <el-button type="success" @click="handleRefresh">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </el-space>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="盘点编号">
          <el-input v-model="searchForm.stocktakeNo" placeholder="请输入盘点编号" clearable />
        </el-form-item>
        <el-form-item label="店铺">
          <el-select v-model="searchForm.storeId" placeholder="请选择店铺" clearable style="width: 200px">
            <el-option label="总店" :value="1" />
            <el-option label="分店 A" :value="2" />
            <el-option label="分店 B" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable style="width: 120px">
            <el-option label="盘点中" :value="0" />
            <el-option label="待审核" :value="1" />
            <el-option label="已完成" :value="2" />
            <el-option label="已取消" :value="4" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table
        v-loading="loading"
        :data="tableData"
        style="width: 100%"
        border
      >
        <el-table-column prop="stocktakeNo" label="盘点编号" width="180" />
        <el-table-column prop="storeName" label="店铺名称" width="120" />
        <el-table-column prop="type" label="盘点类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 1 ? 'primary' : 'success'">
              {{ row.type === 1 ? '周期盘点' : '即时盘点' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="totalCount" label="盘点总数" width="100" />
        <el-table-column prop="diffCount" label="差异数" width="100">
          <template #default="{ row }">
            <el-tag :type="row.diffCount > 0 ? 'danger' : 'success'">
              {{ row.diffCount }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180" />
        <el-table-column prop="operatorName" label="创建人" width="100" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleViewItems(row)">
              明细
            </el-button>
            <el-button
              v-if="row.status === 0"
              type="success"
              link
              size="small"
              @click="handleComplete(row)"
            >
              完成
            </el-button>
            <el-button
              v-if="row.status === 1"
              type="success"
              link
              size="small"
              @click="handleApprove(row)"
            >
              通过
            </el-button>
            <el-button
              v-if="row.status === 1"
              type="danger"
              link
              size="small"
              @click="handleReject(row)"
            >
              拒绝
            </el-button>
            <el-button
              v-if="row.status === 0"
              type="danger"
              link
              size="small"
              @click="handleCancel(row)"
            >
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.size"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 新建盘点对话框 -->
    <el-dialog v-model="createDialogVisible" title="新建盘点" width="500px">
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="100px">
        <el-form-item label="店铺" prop="storeId">
          <el-select v-model="createForm.storeId" placeholder="请选择店铺" style="width: 100%">
            <el-option label="总店" :value="1" />
            <el-option label="分店 A" :value="2" />
            <el-option label="分店 B" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="盘点类型" prop="type">
          <el-radio-group v-model="createForm.type">
            <el-radio :label="1">周期盘点</el-radio>
            <el-radio :label="2">即时盘点</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="createForm.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateSubmit" :loading="createLoading">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 盘点明细对话框 -->
    <el-dialog v-model="itemsDialogVisible" title="盘点明细" width="900px">
      <el-table
        v-loading="itemsLoading"
        :data="itemsTableData"
        style="width: 100%"
        border
      >
        <el-table-column prop="productCode" label="商品编号" width="140" />
        <el-table-column prop="productName" label="商品名称" />
        <el-table-column prop="bookQuantity" label="账面数量" width="100" />
        <el-table-column prop="actualQuantity" label="实际数量" width="100" />
        <el-table-column prop="diffQuantity" label="差异" width="100">
          <template #default="{ row }">
            <el-tag :type="row.diffQuantity === 0 ? 'success' : 'danger'">
              {{ row.diffQuantity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 0 ? 'success' : 'warning'">
              {{ row.status === 0 ? '正常' : '异常' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Search, RefreshLeft } from '@element-plus/icons-vue'

const loading = ref(false)
const tableData = ref([])

const searchForm = reactive({
  stocktakeNo: '',
  storeId: null,
  status: null
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

// 新建盘点对话框
const createDialogVisible = ref(false)
const createLoading = ref(false)
const createFormRef = ref(null)

const createForm = reactive({
  storeId: null,
  type: 1,
  remark: ''
})

const createRules = {
  storeId: [
    { required: true, message: '请选择店铺', trigger: 'change' }
  ],
  type: [
    { required: true, message: '请选择盘点类型', trigger: 'change' }
  ]
}

// 盘点明细对话框
const itemsDialogVisible = ref(false)
const itemsLoading = ref(false)
const itemsTableData = ref([])

const fetchData = async () => {
  loading.value = true
  try {
    // 模拟数据
    tableData.value = [
      {
        stocktakeNo: 'ST2026022418300001',
        storeName: '总店',
        type: 1,
        totalCount: 356,
        diffCount: 5,
        status: 0,
        createdAt: '2026-02-24 18:30:00',
        operatorName: '张店长'
      },
      {
        stocktakeNo: 'ST2026022419300002',
        storeName: '分店 A',
        type: 2,
        totalCount: 128,
        diffCount: 0,
        status: 2,
        createdAt: '2026-02-24 19:30:00',
        operatorName: '李店长'
      }
    ]

    pagination.total = 2
  } catch (error) {
    console.error('获取盘点列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.stocktakeNo = ''
  searchForm.storeId = null
  searchForm.status = null
  handleSearch()
}

const handleRefresh = () => {
  fetchData()
  ElMessage.success('刷新成功')
}

const handleCreate = () => {
  createForm.storeId = null
  createForm.type = 1
  createForm.remark = ''
  createDialogVisible.value = true
}

const handleCreateSubmit = async () => {
  const valid = await createFormRef.value.validate().catch(() => false)
  if (!valid) return

  createLoading.value = true
  try {
    // 模拟提交
    await new Promise(resolve => setTimeout(resolve, 1000))

    ElMessage.success('盘点单创建成功')
    createDialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error('创建盘点单失败:', error)
  } finally {
    createLoading.value = false
  }
}

const handleViewItems = async (row) => {
  itemsDialogVisible.value = true
  itemsLoading.value = true

  try {
    // 模拟数据
    await new Promise(resolve => setTimeout(resolve, 500))

    itemsTableData.value = [
      {
        productCode: 'GJ20260224001',
        productName: '黄金项链 18K',
        bookQuantity: 10,
        actualQuantity: 10,
        diffQuantity: 0,
        status: 0
      },
      {
        productCode: 'GJ20260224002',
        productName: '黄金戒指 18K',
        bookQuantity: 8,
        actualQuantity: 7,
        diffQuantity: -1,
        status: 1
      }
    ]
  } catch (error) {
    console.error('获取盘点明细失败:', error)
  } finally {
    itemsLoading.value = false
  }
}

const handleComplete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要完成盘点「${row.stocktakeNo}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 模拟提交
    await new Promise(resolve => setTimeout(resolve, 1000))

    ElMessage.success('盘点完成')
    fetchData()
  } catch (error) {
    // 取消操作
  }
}

const handleApprove = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要通过盘点「${row.stocktakeNo}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 模拟提交
    await new Promise(resolve => setTimeout(resolve, 1000))

    ElMessage.success('审核通过')
    fetchData()
  } catch (error) {
    // 取消操作
  }
}

const handleReject = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要拒绝盘点「${row.stocktakeNo}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 模拟提交
    await new Promise(resolve => setTimeout(resolve, 1000))

    ElMessage.success('审核拒绝')
    fetchData()
  } catch (error) {
    // 取消操作
  }
}

const handleCancel = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要取消盘点「${row.stocktakeNo}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 模拟提交
    await new Promise(resolve => setTimeout(resolve, 1000))

    ElMessage.success('已取消')
    fetchData()
  } catch (error) {
    // 取消操作
  }
}

const handleSizeChange = (size) => {
  pagination.size = size
  fetchData()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchData()
}

const getStatusLabel = (status) => {
  const labelMap = {
    0: '盘点中',
    1: '待审核',
    2: '已完成',
    3: '已审核',
    4: '已取消'
  }
  return labelMap[status] || status
}

const getStatusTagType = (status) => {
  const typeMap = {
    0: 'primary',
    1: 'warning',
    2: 'success',
    3: 'info',
    4: 'danger'
  }
  return typeMap[status] || ''
}

fetchData()
</script>

<style scoped>
.stocktake-list-container {
  width: 100%;
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
