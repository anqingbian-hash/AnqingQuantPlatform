<template>
  <div class="sales-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>销售记录</span>
          <el-space>
            <el-button type="primary" @click="handleCreateOrder">
              <el-icon><ShoppingCart /></el-icon>
              销售开单
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
        <el-form-item label="订单编号">
          <el-input v-model="searchForm.orderNo" placeholder="请输入订单编号" clearable />
        </el-form-item>
        <el-form-item label="客户姓名">
          <el-input v-model="searchForm.customerName" placeholder="请输入客户姓名" clearable />
        </el-form-item>
        <el-form-item label="店铺">
          <el-select v-model="searchForm.storeId" placeholder="请选择店铺" clearable style="width: 200px">
            <el-option label="总店" :value="1" />
            <el-option label="分店 A" :value="2" />
            <el-option label="分店 B" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
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
        <el-table-column prop="orderNo" label="订单编号" width="180" />
        <el-table-column prop="customerName" label="客户姓名" width="120" />
        <el-table-column prop="customerPhone" label="客户电话" width="120" />
        <el-table-column prop="itemCount" label="商品数量" width="100" />
        <el-table-column prop="totalAmount" label="订单金额" width="120" sortable>
          <template #default="{ row }">
            <span style="color: #e6a23c; font-weight: bold;">
              ¥{{ row.totalAmount.toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="paymentMethod" label="支付方式" width="100">
          <template #default="{ row }">
            <el-tag :type="getPaymentTagType(row.paymentMethod)">
              {{ getPaymentMethodLabel(row.paymentMethod) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="paymentStatus" label="支付状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.paymentStatus === 1 ? 'success' : 'warning'">
              {{ row.paymentStatus === 1 ? '已支付' : '未支付' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="订单状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getOrderStatusTagType(row.status)">
              {{ getOrderStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleViewDetail(row)">
              详情
            </el-button>
            <el-button type="primary" link size="small" @click="handlePrint(row)">
              打印
            </el-button>
            <el-button
              v-if="row.status === 0"
              type="warning"
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

    <!-- 销售开单对话框 -->
    <el-dialog v-model="orderDialogVisible" title="销售开单" width="800px" :close-on-click-modal="false">
      <el-form ref="orderFormRef" :model="orderForm" :rules="orderRules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户姓名">
              <el-input v-model="orderForm.customerName" placeholder="请输入客户姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="客户电话">
              <el-input v-model="orderForm.customerPhone" placeholder="请输入客户电话" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="支付方式">
          <el-radio-group v-model="orderForm.paymentMethod">
            <el-radio label="wechat">微信</el-radio>
            <el-radio label="alipay">支付宝</el-radio>
            <el-radio label="cash">现金</el-radio>
            <el-radio label="card">刷卡</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-divider content-position="left">商品列表</el-divider>

        <el-form-item>
          <el-button type="primary" @click="handleAddProduct">
            <el-icon><Plus /></el-icon>
            添加商品
          </el-button>
        </el-form-item>

        <el-table :data="orderForm.items" border style="width: 100%">
          <el-table-column prop="productCode" label="商品编号" width="140" />
          <el-table-column prop="productName" label="商品名称" />
          <el-table-column prop="weight" label="金重(克)" width="100" />
          <el-table-column prop="purity" label="成色" width="100" />
          <el-table-column prop="unitPrice" label="单价" width="120" />
          <el-table-column prop="quantity" label="数量" width="100" />
          <el-table-column prop="totalPrice" label="小计" width="120" />
          <el-table-column label="操作" width="80">
            <template #default="{ $index }">
              <el-button type="danger" link @click="handleRemoveItem($index)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-row style="margin-top: 20px;">
          <el-col :span="16">
            <el-form-item label="备注">
              <el-input v-model="orderForm.remark" type="textarea" :rows="2" placeholder="请输入备注" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <div class="order-summary">
              <div class="summary-item">
                <span class="label">商品总额：</span>
                <span class="value">¥{{ orderTotalAmount.toFixed(2) }}</span>
              </div>
              <div class="summary-item">
                <span class="label">实收金额：</span>
                <span class="value" style="font-size: 20px; font-weight: bold; color: #e6a23c;">
                  ¥{{ orderTotalAmount.toFixed(2) }}
                </span>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="orderDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleOrderSubmit" :loading="orderLoading">
          确认开单
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ShoppingCart, Refresh, Search, RefreshLeft, Plus } from '@element-plus/icons-vue'
import { CodeGenerator } from '@/utils/code'

const loading = ref(false)
const tableData = ref([])

const searchForm = reactive({
  orderNo: '',
  customerName: '',
  storeId: 1
})

const dateRange = ref([])

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

// 销售开单对话框
const orderDialogVisible = ref(false)
const orderLoading = ref(false)
const orderFormRef = ref(null)
const orderForm = reactive({
  customerName: '',
  customerPhone: '',
  paymentMethod: 'wechat',
  items: [],
  remark: ''
})

const orderRules = {}

const orderTotalAmount = computed(() => {
  return orderForm.items.reduce((sum, item) => sum + item.totalPrice, 0)
})

const fetchData = async () => {
  loading.value = true
  try {
    // 模拟数据
    tableData.value = [
      {
        orderNo: 'SO2026022418300001',
        customerName: '张三',
        customerPhone: '13800138000',
        itemCount: 2,
        totalAmount: 158600,
        paymentMethod: 'wechat',
        paymentStatus: 1,
        status: 1,
        createdAt: '2026-02-24 18:30:00'
      },
      {
        orderNo: 'SO2026022418300002',
        customerName: '李四',
        customerPhone: '13800138001',
        itemCount: 1,
        totalAmount: 89600,
        paymentMethod: 'alipay',
        paymentStatus: 1,
        status: 1,
        createdAt: '2026-02-24 18:35:00'
      }
    ]

    pagination.total = 23
  } catch (error) {
    console.error('获取销售记录失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.orderNo = ''
  searchForm.customerName = ''
  searchForm.storeId = 1
  dateRange.value = []
  handleSearch()
}

const handleRefresh = () => {
  fetchData()
  ElMessage.success('刷新成功')
}

const handleCreateOrder = () => {
  orderForm.customerName = ''
  orderForm.customerPhone = ''
  orderForm.paymentMethod = 'wechat'
  orderForm.items = []
  orderForm.remark = ''
  orderDialogVisible.value = true
}

const handleAddProduct = () => {
  ElMessage.info('添加商品功能开发中')
}

const handleRemoveItem = (index) => {
  orderForm.items.splice(index, 1)
}

const handleOrderSubmit = async () => {
  if (orderForm.items.length === 0) {
    ElMessage.warning('请先添加商品')
    return
  }

  orderLoading.value = true
  try {
    // 模拟提交
    await new Promise(resolve => setTimeout(resolve, 1000))

    ElMessage.success('开单成功')
    orderDialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error('开单失败:', error)
  } finally {
    orderLoading.value = false
  }
}

const handleViewDetail = (row) => {
  ElMessage.info('查看详情功能开发中')
}

const handlePrint = (row) => {
  ElMessage.info('打印功能开发中')
}

const handleCancel = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要取消订单「${row.orderNo}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    ElMessage.success('取消成功')
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

const getPaymentTagType = (method) => {
  const typeMap = {
    wechat: 'success',
    alipay: 'primary',
    cash: 'warning',
    card: 'info'
  }
  return typeMap[method] || ''
}

const getPaymentMethodLabel = (method) => {
  const labelMap = {
    wechat: '微信',
    alipay: '支付宝',
    cash: '现金',
    card: '刷卡'
  }
  return labelMap[method] || method
}

const getOrderStatusTagType = (status) => {
  const typeMap = {
    0: 'warning',
    1: 'success',
    2: 'info'
  }
  return typeMap[status] || ''
}

const getOrderStatusLabel = (status) => {
  const labelMap = {
    0: '待支付',
    1: '已完成',
    2: '已取消'
  }
  return labelMap[status] || status
}

fetchData()
</script>

<style scoped>
.sales-list-container {
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

.order-summary {
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.summary-item:last-child {
  margin-bottom: 0;
}

.summary-item .label {
  color: #666;
}

.summary-item .value {
  font-weight: bold;
}
</style>
