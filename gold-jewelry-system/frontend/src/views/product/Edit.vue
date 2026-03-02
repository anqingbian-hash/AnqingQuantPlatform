<template>
  <div class="product-edit-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>编辑商品</span>
          <el-button @click="handleBack">
            <el-icon><Back /></el-icon>
            返回
          </el-button>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="product-form"
      >
        <el-form-item label="商品编号" prop="productCode">
          <el-input v-model="form.productCode" placeholder="请输入商品编号" disabled />
        </el-form-item>

        <el-form-item label="商品名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入商品名称" />
        </el-form-item>

        <el-form-item label="商品分类" prop="categoryId">
          <el-select v-model="form.categoryId" placeholder="请选择分类" style="width: 100%">
            <el-option label="黄金项链" :value="1" />
            <el-option label="黄金戒指" :value="2" />
            <el-option label="黄金手镯" :value="3" />
            <el-option label="白银项链" :value="4" />
            <el-option label="白银戒指" :value="5" />
            <el-option label="白银手镯" :value="6" />
          </el-select>
        </el-form-item>

        <el-form-item label="金重（克）" prop="weight">
          <el-input-number
            v-model="form.weight"
            :min="0"
            :precision="2"
            :step="0.01"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="成色" prop="purity">
          <el-select v-model="form.purity" placeholder="请选择成色" style="width: 100%">
            <el-option label="Au99.99" value="Au99.99" />
            <el-option label="Au99.95" value="Au99.95" />
            <el-option label="Au99.5" value="Au99.5" />
            <el-option label="Au99" value="Au99" />
            <el-option label="Au91.6" value="Au91.6" />
            <el-option label="Au75" value="Au75" />
          </el-select>
        </el-form-item>

        <el-form-item label="工费（元）" prop="craftFee">
          <el-input-number
            v-model="form.craftFee"
            :min="0"
            :precision="2"
            :step="10"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="证书编号" prop="certificateNo">
          <el-input v-model="form.certificateNo" placeholder="请输入证书编号" />
        </el-form-item>

        <el-form-item label="图片" prop="imageUrl">
          <el-upload
            class="avatar-uploader"
            :show-file-list="false"
            :on-success="handleUploadSuccess"
            :before-upload="beforeUpload"
          >
            <img v-if="form.imageUrl" :src="form.imageUrl" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>

        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="form.remark"
            type="textarea"
            :rows="4"
            placeholder="请输入备注"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">
            提交
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back, Plus } from '@element-plus/icons-vue'
import { getProductByCode, updateProduct } from '@/api/product'

const router = useRouter()
const route = useRoute()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  id: null,
  productCode: '',
  name: '',
  categoryId: null,
  weight: 0,
  purity: 'Au99.99',
  craftFee: 0,
  certificateNo: '',
  imageUrl: '',
  remark: ''
})

const rules = {
  name: [
    { required: true, message: '请输入商品名称', trigger: 'blur' }
  ],
  categoryId: [
    { required: true, message: '请选择商品分类', trigger: 'change' }
  ],
  weight: [
    { required: true, message: '请输入金重', trigger: 'blur' }
  ],
  purity: [
    { required: true, message: '请选择成色', trigger: 'change' }
  ],
  craftFee: [
    { required: true, message: '请输入工费', trigger: 'blur' }
  ]
}

const fetchData = async () => {
  try {
    const res = await getProductByCode(route.params.id)
    if (res.code === 200) {
      Object.assign(form, res.data)
    }
  } catch (error) {
    console.error('获取商品信息失败:', error)
  }
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await updateProduct(form.id, form)
    if (res.code === 200) {
      ElMessage.success('更新成功')
      router.push('/products')
    }
  } catch (error) {
    console.error('更新商品失败:', error)
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  fetchData()
}

const handleBack = () => {
  router.back()
}

const beforeUpload = (file) => {
  const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isJPG) {
    ElMessage.error('只能上传 JPG/PNG 格式的图片!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }
  return true
}

const handleUploadSuccess = (res) => {
  form.imageUrl = res.data.url
  ElMessage.success('上传成功')
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.product-edit-container {
  width: 100%;
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.product-form {
  max-width: 800px;
}

.avatar-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
}

.avatar-uploader:hover {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  line-height: 178px;
  text-align: center;
}

.avatar {
  width: 178px;
  height: 178px;
  display: block;
}
</style>
