<template>
  <el-container class="layout-container">
    <el-aside width="200px" class="layout-aside">
      <div class="logo">
        <h2>金饰管理系统</h2>
      </div>

      <el-menu
        :default-active="activeMenu"
        router
        class="layout-menu"
        background-color="#2c3e50"
        text-color="#ecf0f1"
        active-text-color="#D4AF37"
      >
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>

        <el-sub-menu index="product">
          <template #title>
            <el-icon><Box /></el-icon>
            <span>商品管理</span>
          </template>
          <el-menu-item index="/products">
            <el-icon><List /></el-icon>
            <span>商品列表</span>
          </el-menu-item>
          <el-menu-item index="/products/add">
            <el-icon><Plus /></el-icon>
            <span>添加商品</span>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="inventory">
          <template #title>
            <el-icon><Goods /></el-icon>
            <span>库存管理</span>
          </template>
          <el-menu-item index="/inventory">
            <el-icon><List /></el-icon>
            <span>库存列表</span>
          </el-menu-item>
          <el-menu-item index="/stocktake">
            <el-icon><Notebook /></el-icon>
            <span>库存盘点</span>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="sales">
          <template #title>
            <el-icon><ShoppingCart /></el-icon>
            <span>销售管理</span>
          </template>
          <el-menu-item index="/sales">
            <el-icon><List /></el-icon>
            <span>销售记录</span>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="stores">
          <template #title>
            <el-icon><Shop /></el-icon>
            <span>多店管理</span>
          </template>
          <el-menu-item index="/stores">
            <el-icon><List /></el-icon>
            <span>店铺列表</span>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>{{ currentRoute.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><User /></el-icon>
              <span>{{ userInfo.realName || '管理员' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  HomeFilled,
  Box,
  List,
  Plus,
  Goods,
  Notebook,
  ShoppingCart,
  User,
  ArrowDown,
  Shop
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || '{}'))

const activeMenu = computed(() => route.path)

const handleCommand = async (command) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人信息功能开发中')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        router.push('/login')
        ElMessage.success('已退出登录')
      } catch {
        // 取消操作
      }
      break
  }
}
</script>

<style scoped>
.layout-container {
  width: 100%;
  height: 100vh;
}

.layout-aside {
  background-color: #2c3e50;
  color: #ecf0f1;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #34495e;
}

.logo h2 {
  font-size: 18px;
  color: #D4AF37;
}

.layout-menu {
  border-right: none;
}

.layout-header {
  background-color: #fff;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f5f5;
}

.layout-main {
  background-color: #f5f5f5;
  padding: 20px;
}
</style>
