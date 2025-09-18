<template>
  <div class="user-management">
    <div class="page-header">
      <h1 class="page-title">用户管理</h1>
      <p class="page-subtitle">管理系统用户和权限</p>
    </div>

    <div class="user-content">
      <!-- 用户列表 -->
      <el-card class="user-card">
        <template #header>
          <div class="card-header">
            <h3 class="card-title">用户列表</h3>
            <div class="header-actions">
              <el-button @click="refreshUsers" :loading="loading">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </div>
        </template>

        <el-table :data="users" style="width: 100%" v-loading="loading">
          <el-table-column prop="account" label="账号" width="120" />
          <el-table-column prop="role" label="角色" width="100">
            <template #default="{ row }">
              <el-tag :type="getRoleTagType(row.role)">
                {{ getRoleText(row.role) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status)">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="email" label="邮箱" width="200" />
          <el-table-column prop="phone" label="手机" width="120" />
          <el-table-column prop="login_attempts" label="失败次数" width="100" />
          <el-table-column prop="is_locked" label="锁定状态" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.is_locked" type="danger">已锁定</el-tag>
              <el-tag v-else type="success">正常</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="create_time" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.create_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="last_login_time" label="最后登录" width="180">
            <template #default="{ row }">
              {{ formatDate(row.last_login_time) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button 
                v-if="row.is_locked" 
                type="success" 
                size="small" 
                @click="unlockUser(row)"
                :loading="unlockingUsers.includes(row.user_id)"
              >
                解锁
              </el-button>
              <el-button 
                type="primary" 
                size="small" 
                @click="editUserStatus(row)"
              >
                修改状态
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 修改用户状态对话框 -->
    <el-dialog
      v-model="statusDialogVisible"
      title="修改用户状态"
      width="400px"
    >
      <el-form :model="statusForm" label-width="80px">
        <el-form-item label="用户账号">
          <el-input v-model="statusForm.account" disabled />
        </el-form-item>
        <el-form-item label="当前状态">
          <el-tag :type="getStatusTagType(statusForm.currentStatus)">
            {{ getStatusText(statusForm.currentStatus) }}
          </el-tag>
        </el-form-item>
        <el-form-item label="新状态" required>
          <el-select v-model="statusForm.newStatus" placeholder="请选择状态">
            <el-option label="正常" value="active" />
            <el-option label="禁用" value="inactive" />
            <el-option label="锁定" value="locked" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="statusDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="updateUserStatus" :loading="updating">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import api from '../utils/api'

const users = ref([])
const loading = ref(false)
const unlockingUsers = ref([])
const updating = ref(false)

// 状态修改对话框
const statusDialogVisible = ref(false)
const statusForm = ref({
  user_id: '',
  account: '',
  currentStatus: '',
  newStatus: ''
})

// 获取用户列表
const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/users')
    users.value = response.data.users
  } catch (error) {
    ElMessage.error('获取用户列表失败')
    console.error('获取用户列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 刷新用户列表
const refreshUsers = () => {
  fetchUsers()
}

// 解锁用户
const unlockUser = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要解锁用户 "${user.account}" 吗？`,
      '确认解锁',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    unlockingUsers.value.push(user.user_id)
    
    try {
      await api.post(`/admin/users/${user.user_id}/unlock`)
      ElMessage.success('用户解锁成功')
      await fetchUsers() // 刷新列表
    } catch (error) {
      ElMessage.error('解锁失败')
    } finally {
      const index = unlockingUsers.value.indexOf(user.user_id)
      if (index > -1) {
        unlockingUsers.value.splice(index, 1)
      }
    }
  } catch {
    // 用户取消解锁
  }
}

// 编辑用户状态
const editUserStatus = (user) => {
  statusForm.value = {
    user_id: user.user_id,
    account: user.account,
    currentStatus: user.status,
    newStatus: user.status
  }
  statusDialogVisible.value = true
}

// 更新用户状态
const updateUserStatus = async () => {
  if (statusForm.value.newStatus === statusForm.value.currentStatus) {
    ElMessage.warning('状态未发生变化')
    return
  }
  
  updating.value = true
  try {
    await api.put(`/admin/users/${statusForm.value.user_id}/status`, {
      status: statusForm.value.newStatus
    })
    ElMessage.success('用户状态更新成功')
    statusDialogVisible.value = false
    await fetchUsers() // 刷新列表
  } catch (error) {
    ElMessage.error('更新用户状态失败')
  } finally {
    updating.value = false
  }
}

// 获取角色标签类型
const getRoleTagType = (role) => {
  const types = {
    'admin': 'danger',
    'analyst': 'warning',
    'viewer': 'info'
  }
  return types[role] || 'info'
}

// 获取角色文本
const getRoleText = (role) => {
  const texts = {
    'admin': '管理员',
    'analyst': '分析师',
    'viewer': '普通用户'
  }
  return texts[role] || role
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  const types = {
    'active': 'success',
    'inactive': 'warning',
    'locked': 'danger'
  }
  return types[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const texts = {
    'active': '正常',
    'inactive': '禁用',
    'locked': '锁定'
  }
  return texts[status] || status
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchUsers()
})
</script>

<style lang="scss" scoped>
.user-management {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 20px;
  text-align: center;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.page-subtitle {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
}

.user-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.user-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .card-title {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
  }
  
  .header-actions {
    display: flex;
    gap: 10px;
  }
}
</style>
