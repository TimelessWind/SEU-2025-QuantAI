import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('../layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('../views/Home.vue'),
        meta: { title: '首页' }
      },
      {
        path: '/stock-filter',
        name: 'StockFilter',
        component: () => import('../views/StockFilter.vue'),
        meta: { title: '股票筛选' }
      },
      {
        path: '/strategy',
        name: 'Strategy',
        component: () => import('../views/Strategy.vue'),
        meta: { title: '策略管理' }
      },
      {
        path: '/backtest',
        name: 'Backtest',
        component: () => import('../views/Backtest.vue'),
        meta: { title: '回测分析' }
      },
      {
        path: '/user-management',
        name: 'UserManagement',
        component: () => import('../views/UserManagement.vue'),
        meta: { title: '用户管理', requiresAdmin: true }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && userStore.isAuthenticated) {
    next('/')
  } else if (to.meta.requiresAdmin && !userStore.isAdmin) {
    // 检查管理员权限
    next('/')
  } else {
    next()
  }
})

export default router
