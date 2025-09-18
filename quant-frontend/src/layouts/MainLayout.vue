<template>
  <div class="main-layout">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside :width="isCollapse ? '64px' : '240px'" class="sidebar">
        <div class="logo">
          <el-icon v-if="isCollapse"><TrendCharts /></el-icon>
          <span v-else>量化交易系统</span>
        </div>
        
        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :unique-opened="true"
          router
          class="sidebar-menu"
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <template #title>首页</template>
          </el-menu-item>
          
          <el-menu-item index="/stock-filter">
            <el-icon><Filter /></el-icon>
            <template #title>股票筛选</template>
          </el-menu-item>
          
          <el-menu-item index="/strategy">
            <el-icon><Setting /></el-icon>
            <template #title>策略管理</template>
          </el-menu-item>
          
          <el-menu-item index="/backtest">
            <el-icon><DataAnalysis /></el-icon>
            <template #title>回测分析</template>
          </el-menu-item>
          
          <el-menu-item v-if="userStore.isAdmin" index="/user-management">
            <el-icon><UserFilled /></el-icon>
            <template #title>用户管理</template>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <!-- 主内容区 -->
      <el-container>
        <!-- 顶部导航 -->
        <el-header class="header">
          <div class="header-left">
            <el-button
              type="text"
              @click="toggleCollapse"
              class="collapse-btn"
            >
              <el-icon>
                <Expand v-if="isCollapse" />
                <Fold v-else />
              </el-icon>
            </el-button>
            
            <el-breadcrumb separator="/" class="breadcrumb">
              <el-breadcrumb-item>{{ currentPageTitle }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          
          <div class="header-right">
            <el-dropdown @command="handleCommand">
              <div class="user-info">
                <el-avatar :size="32">
                  <el-icon><User /></el-icon>
                </el-avatar>
                <span class="username">{{ userStore.userInfo?.account || '用户' }}</span>
                <el-icon class="arrow-down"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>
                    个人资料
                  </el-dropdown-item>
                  <el-dropdown-item command="settings">
                    <el-icon><Setting /></el-icon>
                    系统设置
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        
        <!-- 主内容 -->
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isCollapse = ref(false)

const activeMenu = computed(() => route.path)

const currentPageTitle = computed(() => {
  return route.meta?.title || '首页'
})

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      // 跳转到个人资料页面
      break
    case 'settings':
      // 跳转到设置页面
      break
    case 'logout':
      userStore.logout()
      router.push('/login')
      break
  }
}

// 监听路由变化，自动收起侧边栏（移动端）
watch(route, () => {
  if (window.innerWidth <= 768) {
    isCollapse.value = true
  }
})
</script>

<style lang="scss" scoped>
.main-layout {
  height: 100vh;
}

.sidebar {
  background: var(--background-white);
  border-right: 1px solid var(--border-light);
  transition: width 0.3s ease;
  
  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-bottom: 1px solid var(--border-lighter);
    font-size: 18px;
    font-weight: 600;
    color: var(--primary-color);
    background: var(--background-light);
  }
  
  .sidebar-menu {
    border: none;
    height: calc(100vh - 60px);
  }
}

.header {
  background: var(--background-white);
  border-bottom: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  
  .header-left {
    display: flex;
    align-items: center;
    
    .collapse-btn {
      margin-right: 20px;
      font-size: 18px;
      color: var(--text-regular);
      
      &:hover {
        color: var(--primary-color);
      }
    }
    
    .breadcrumb {
      font-size: 16px;
    }
  }
  
  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      cursor: pointer;
      padding: 8px 12px;
      border-radius: 6px;
      transition: all 0.3s ease;
      
      &:hover {
        background: var(--background-light);
      }
      
      .username {
        margin: 0 8px;
        font-size: 14px;
        color: var(--text-primary);
      }
      
      .arrow-down {
        font-size: 12px;
        color: var(--text-secondary);
      }
    }
  }
}

.main-content {
  background: var(--background-base);
  padding: 0;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    
    &.show {
      transform: translateX(0);
    }
  }
  
  .header {
    padding: 0 15px;
    
    .header-left {
      .breadcrumb {
        display: none;
      }
    }
  }
}
</style>


