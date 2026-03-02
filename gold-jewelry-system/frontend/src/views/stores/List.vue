<template>
  <div class="stores-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>店铺管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            添加店铺
          </el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="店铺名称">
          <el-input v-model="searchForm.name" placeholder="请输入店铺名称" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable style="width: 150px">
            <el-option label="启用" :value="1" />
            <el-option label="禁用" :value="0" />
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
        <el-table-column prop="id" label="店铺 ID" width="80" />
        <el-table-column prop="name" label="店铺名称" />
        <el-table-column prop="address" label="店铺地址" />
        <el-table-column prop="phone" label="联系电话" width="120" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button
              v-if="row.status === 1"
              type="warning"
              link
              size="small"
              @click="handleDisable(row)"
            >
              禁用
            </el-button>
            <el-button
              v-if="row.status === 0"
              type="success"
              link
              size="small"
              @click="handleEnable(row)"
            >
              启用
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑店铺' : '添加店铺'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="店铺名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入店铺名称" />
        </el-form-item>

        <el-form-item label="店铺地址" prop="address">
          <el-input v-model="form.address" placeholder="请输入店铺地址" />
        </el-form-item>

        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入联系电话" />
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :label="1">启用</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, RefreshLeft } from '@element-plus/icons-vue'
import { getAllStores } from '@/api/store'

const loading = ref(false)
const tableData = ref([])

const searchForm = reactive({
  name: '',
  status: null
})

// 对话框
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)

const form = reactive({
  id: null,
  name: '',
  address: '',
  phone: '',
  status: 1
})

const rules = {
  name: [
    { required: true, message: '请输入店铺名称', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ]
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getAllStores()
    if (res.code === 200) {
      tableData.value = res.data
    }
  } catch (error) {
    console.error('获取店铺列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  // 过滤逻辑
  let filtered = [...tableData.value]

  if (searchForm.name) {
    filtered = filtered.filter(item => item.name.includes(searchForm.name))
  }

  if (searchForm.status !== null) {
    filtered = filtered.filter(item => item.status === searchForm.status)
  }

  // 更新表格数据
  tableData.value = filtered
}

const handleReset = () => {
  searchForm.name = ''
  searchForm.status = null
  fetchData()
}

const handleAdd = () => {
  form.id = null
  form.name = ''
  form.address = ''
  form.phone = ''
  form.status = 1
  isEdit.value = false
  dialogVisible.value = true
}

const handleEdit = (row) => {
  form.id = row.id
  form.name = row.name
  form.address = row.address
  form.phone = row.phone
  form.status = row.status
  isEdit.value = true
  dialogVisible.value = true
}

const handleDisable = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要禁用店铺「${row.name}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    row.status = 0
    ElMessage.success('禁用成功')
  } catch (error) {
    // 取消操作
  }
}

const handleEnable = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要启用店铺「${row.name}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    row.status = 1
    ElMessage.success('启用成功')
  } catch (error) {
    // 取消操作
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除店铺「${row.name}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 实际项目中应该调用删除 API
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    // 取消操作
  }
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    // 模拟提交
    await new Promise(resolve => setTimeout(resolve, 1000))

    if (isEdit.value) {
      ElMessage.success('更新成功')
    } else {
      ElMessage.success('添加成功')
    }

    dialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitLoading.value = false
  }
}

fetchData()
</script>

<style scoped>
.stores-list-container {
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
