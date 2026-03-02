<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #409eff">
              <el-icon :size="32"><Box /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.productCount }}</div>
              <div class="stat-label">商品总数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #67c23a">
              <el-icon :size="32"><Goods /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.inventoryCount }}</div>
              <div class="stat-label">库存总数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #e6a23c">
              <el-icon :size="32"><ShoppingCart /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.salesCount }}</div>
              <div class="stat-label">今日销售</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #f56c6c">
              <el-icon :size="32"><Money /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">¥{{ stats.salesAmount }}</div>
              <div class="stat-label">今日销售额</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>实时金价</span>
              <el-button type="primary" size="small" @click="refreshGoldPrice">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          <div class="gold-price-content">
            <div class="gold-price-value">
              <span class="label">当前金价：</span>
              <span class="value">¥{{ goldPrice }}</span>
              <span class="unit">元/克</span>
            </div>
            <div class="gold-price-time">
              更新时间：{{ goldPriceTime }}
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <span>低库存预警</span>
          </template>
          <el-table :data="lowStockList" style="width: 100%">
            <el-table-column prop="productCode" label="商品编号" width="120" />
            <el-table-column prop="productName" label="商品名称" />
            <el-table-column prop="quantity" label="库存数量" width="100" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Box, Goods, ShoppingCart, Money, Refresh } from '@element-plus/icons-vue'
import { getGoldPrice } from '@/api/price'
import { ElMessage } from 'element-plus'

const stats = ref({
  productCount: 0,
  inventoryCount: 0,
  salesCount: 0,
  salesAmount: 0
})

const goldPrice = ref('0.00')
const goldPriceTime = ref('-')

const lowStockList = ref([])

const refreshGoldPrice = async () => {
  try {
    const res = await getGoldPrice()
    if (res.code === 200) {
      goldPrice.value = res.data.toFixed(2)
      goldPriceTime.value = new Date().toLocaleString()
      ElMessage.success('金价更新成功')
    }
  } catch (error) {
    ElMessage.error('金价更新失败')
  }
}

onMounted(() => {
  // 模拟数据
  stats.value = {
    productCount: 128,
    inventoryCount: 356,
    salesCount: 23,
    salesAmount: 158600
  }

  lowStockList.value = [
    { productCode: 'GJ20260224001', productName: '黄金项链 18K', quantity: 3 },
    { productCode: 'GJ20260224005', productName: '白银戒指 925', quantity: 5 }
  ]

  refreshGoldPrice()
})
</script>

<style scoped>
.dashboard-container {
  width: 100%;
  height: 100%;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #999;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.gold-price-content {
  padding: 20px 0;
}

.gold-price-value {
  font-size: 24px;
  margin-bottom: 12px;
}

.gold-price-value .label {
  color: #666;
  font-size: 16px;
}

.gold-price-value .value {
  color: #e6a23c;
  font-weight: bold;
  font-size: 32px;
  margin: 0 8px;
}

.gold-price-value .unit {
  color: #999;
  font-size: 14px;
}

.gold-price-time {
  color: #999;
  font-size: 12px;
}
</style>
