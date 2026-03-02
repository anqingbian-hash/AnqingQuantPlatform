import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/layout/Index.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '首页' }
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('@/views/product/List.vue'),
        meta: { title: '商品管理' }
      },
      {
        path: 'products/add',
        name: 'ProductAdd',
        component: () => import('@/views/product/Add.vue'),
        meta: { title: '添加商品' }
      },
      {
        path: 'products/edit/:id',
        name: 'ProductEdit',
        component: () => import('@/views/product/Edit.vue'),
        meta: { title: '编辑商品' }
      },
      {
        path: 'inventory',
        name: 'Inventory',
        component: () => import('@/views/inventory/List.vue'),
        meta: { title: '库存管理' }
      },
      {
        path: 'stocktake',
        name: 'Stocktake',
        component: () => import('@/views/inventory/Stocktake.vue'),
        meta: { title: '库存盘点' }
      },
      {
        path: 'sales',
        name: 'Sales',
        component: () => import('@/views/sales/List.vue'),
        meta: { title: '销售管理' }
      },
      {
        path: 'stores',
        name: 'Stores',
        component: () => import('@/views/stores/List.vue'),
        meta: { title: '店铺管理' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 黄金白银贵金属首饰管理系统` : '黄金白银贵金属首饰管理系统'

  // 检查是否需要登录
  if (to.path !== '/login') {
    const token = localStorage.getItem('token')
    if (!token) {
      next('/login')
      return
    }
  }

  next()
})

export default router
