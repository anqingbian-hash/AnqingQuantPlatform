<template>
  <div class="inventory-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>库存列表</span>
          <el-space>
            <el-button type="primary" @click="handleStockIn">
              <el-icon><Plus /></el-icon>
              入库
            </el-button>
            <el-button type="warning" @click="handleStockOut">
              <el-icon><Minus /></el-icon>
              出库
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
        <el-form-item label="商品编号">
          <el-input v-model="searchForm.productCode" placeholder="请输入商品编号" clearable />
        </el-form-item>
        <el-form-item label="店铺">
          <el-select v-model="searchForm.storeId" placeholder="请选择店铺" clearable style="width: 200px">
            <el-option label="总店" :value="1" />
            <el-option label="分店 A" :value="2" />
            <el-option label="分店 B" :value="3" />
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
        :summary-method="getSummaries"
        show-summary
      >
        <el-table-column prop="productCode" label="商品编号" width="140" />
        <el-table-column prop="productName" label="商品名称" />
        <el-table-column prop="weight" label="金重(克)" width="100" />
        <el-table-column prop="purity" label="成色" width="100" />
        <el-table-column prop="quantity" label="库存数量" width="120" sortable>
          <template #default="{ row }">
            <el-tag :type="getStockTagType(row.quantity)">
              {{ row.quantity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="frozenQuantity" label="冻结数量" width="120" />
        <el-table-column prop="updatedAt" label="更新时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleViewLogs(row)">
              流水
            </el-button>
            <el-button type="primary" link size="small" @click="handleStockInItem(row)">
              入库
            </el-button>
            <el-button type="warning" link size="small" @click="handleStockOutItem(row)">
              出库
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 入库对话框 -->
    <el-dialog v-model="stockInDialogVisible" title="入库" width="500px">
      <el-form ref="stockInFormRef" :model="stockInForm" :rules="stockInRules" label-width="100px">
        <el-form-item label="商品编号" prop="productId">
          <el-input v-model="stockInForm.productCode" placeholder="请输入商品编号" disabled />
        </el-form-item>
        <el-form-item label="入库数量" prop="quantity">
          <el-input-number v-model="stockInForm.quantity" :min="1" :max="1000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="关联单号">
          <el-input v-model="stockInForm.orderNo" placeholder="请输入关联单号" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="stockInForm.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stockInDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleStockInSubmit" :loading="stockInLoading">
          确认入库
        </el-button>
      </template>
    </el-dialog>

    <!-- 出库对话框 -->
    <el-dialog v-model="stockOutDialogVisible" title="出库" width="500px">
      <el-form ref="stockOutFormRef" :model="stockOutForm" :rules="stockOutRules" label-width="100px">
        <el-form-item label="商品编号" prop="productId">
          <el-input v-model="stockOutForm.productCode" placeholder="请输入商品编号" disabled />
        </el-form-item>
        <el-form-item label="出库数量" prop="quantity">
          <el-input-number v-model="stockOutForm.quantity" :min="1" :max="stockOutForm.maxQuantity" style="width: 100%" />
        </el-form-item>
        <el-form-item label="关联单号">
          <el-input v-model="stockOutForm.orderNo" placeholder="请输入关联单号" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="stockOutForm.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stockOutDialogVisible = false">取消</el-button>
        <el-button type="warning" @click="handleStockOutSubmit" :loading="stockOutLoading">
          确认出库
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Minus, Refresh, Search, RefreshLeft } from '@element-plus/icons-vue'
import { getInventoryByStore, stockIn, stockOut } from '@/api/inventory'
import { CodeGenerator } from '@/utils/code'

const loading = ref(false)
const tableData = ref([])

const searchForm = reactive({
  productCode: '',
  storeId: 1
})

// 入库对话框
const stockInDialogVisible = ref(false)
const stockInLoading = ref(false)
const stockInFormRef = ref(null)
const stockInForm = reactive({
  productId: null,
  productCode: '',
  quantity: 1,
  orderNo: CodeGenerator.generateOrderNo(),
  remark: ''
})

const stockInRules = {
  productId: [
    { required: true, message: '请选择商品', trigger: 'change' }
  ],
  quantity: [
    { required: true, message: '请输入入库数量', trigger: 'blur' }
  ]
}

// 出库对话框
const stockOutDialogVisible = ref(false)
const stockOutLoading = ref(false)
const stockOutFormRef = ref(null)
const stockOutForm = reactive({
  productId: null,
  productCode: '',
  quantity: 1,
  maxQuantity: 999,
  orderNo: CodeGenerator.generateOrderNo(),
  remark: ''
})

const stockOutRules = {
  productId: [
    { required: true, message: '请选择商品', trigger: 'change' }
  ],
  quantity: [
    { required: true, message: '请输入出库数量', trigger: 'blur' }
  ]
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getInventoryByStore(searchForm.storeId)
    if (res.code === 200) {
      tableData.value = res.data.map(item => ({
        ...item,
        productCode: 'GJ20260224001', // 模拟商品编号
        productName: '黄金项链 18K', // 模拟商品名称
        weight: 10.5, // 模拟金重
        purity: 'Au99.99' // 模拟成色
      }))
    }
  } catch (error) {
    console.error('获取库存列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  fetchData()
}

const handleReset = () => {
  searchForm.productCode = ''
  searchForm.storeId = 1
  fetchData()
}

const handleRefresh = () => {
  fetchData()
  ElMessage.success('刷新成功')
}

const handleStockIn = () => {
  stockInForm.productId = null
  stockInForm.productCode = ''
  stockInForm.quantity = 1
  stockInForm.orderNo = CodeGenerator.generateOrderNo()
  stockInForm.remark = ''
  stockInDialogVisible.value = true
}

const handleStockOut = () => {
  stockOutForm.productId = null
  stockOutForm.productCode = ''
  stockOutForm.quantity = 1
  stockOutForm.maxQuantity = 999
  stockOutForm.orderNo = CodeGenerator.generateOrderNo()
  stockOutForm.remark = ''
  stockOutDialogVisible.value = true
}

const handleStockInItem = (row) => {
  stockInForm.productId = row.productId
  stockInForm.productCode = row.productCode
  stockInForm.quantity = 1
  stockInForm.orderNo = CodeGenerator.generateOrderNo()
  stockInForm.remark = ''
  stockInDialogVisible.value = true
}

const handleStockOutItem = (row) => {
  stockOutForm.productId = row.productId
  stockOutForm.productCode = row.productCode
  stockOutForm.quantity = 1
  stockOutForm.maxQuantity = row.quantity
  stockOutForm.orderNo = CodeGenerator.generateOrderNo()
  stockOutForm.remark = ''
  stockOutDialogVisible.value = true
}

const handleStockInSubmit = async () => {
  const valid = await stockInFormRef.value.validate().catch(() => false)
  if (!valid) return

  stockInLoading.value = true
  try {
    const res = await stockIn({
      productId: stockInForm.productId,
      storeId: searchForm.storeId,
      quantity: stockInForm.quantity,
      operatorId: 1,
      orderNo: stockInForm.orderNo
    })

    if (res.code === 200) {
      ElMessage.success('入库成功')
      stockInDialogVisible.value = false
      fetchData()
    }
  } catch (error) {
    console.error('入库失败:', error)
  } finally {
    stockInLoading.value = false
  }
}

const handleStockOutSubmit = async () => {
  const valid = await stockOutFormRef.value.validate().catch(() => false)
  if (!valid) return

  stockOutLoading.value = true
  try {
    const res = await stockOut({
      productId: stockOutForm.productId,
      storeId: searchForm.storeId,
      quantity: stockOutForm.quantity,
      operatorId: 1,
      orderNo: stockOutForm.orderNo
    })

    if (res.code === 200) {
      ElMessage.success('出库成功')
      stockOutDialogVisible.value = false
      fetchData()
    }
  } catch (error) {
    console.error('出库失败:', error)
  } finally {
    stockOutLoading.value = false
  }
}

const handleViewLogs = (row) => {
  ElMessage.info('查看流水功能开发中')
}

const getStockTagType = (quantity) => {
  if (quantity <= 5) return 'danger'
  if (quantity <= 10) return 'warning'
  return 'success'
}

const getSummaries = (param) => {
  const { columns, data } = param
  const sums = []

  columns.forEach((column, index) => {
    if (index === 0) {
      sums[index] = '合计'
      return
    }

    if (column.property === 'quantity') {
      sums[index] = data.reduce((sum, row) => sum + row.quantity, 0)
      return
    }

    if (column.property === 'frozenQuantity') {
      sums[index] = data.reduce((sum, row) => sum + row.frozenQuantity, 0)
      return
    }

    sums[index] = ''
  })

  return sums
}

fetchData()
</script>

<style scoped>
.inventory-list-container {
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
</style>
