<script setup>
import { useAgentStore } from '../stores/agentStore'
import { storeToRefs } from 'pinia'
import KnowledgeBasePanel from './KnowledgeBasePanel.vue'
import { Monitor, Collection } from '@element-plus/icons-vue'
import { ref } from 'vue'

const store = useAgentStore()
const kbDrawerVisible = ref(false)
import { watch } from 'vue'

const { currentRole } = storeToRefs(store)

watch(currentRole, () => {
    store.resetState()
})
</script>

<template>
  <div class="common-layout">
    <div class="header-bar">
      <div class="logo-area">
        <el-icon :size="24"><Monitor /></el-icon>
        多智能体协同教学系统
      </div>
      <div class="user-info">
        <!-- Internal Test: View As Dropdown -->
        <div v-if="store.realUserRole === 'internal_test'" style="margin-right: 20px; display: flex; align-items: center;">
            <span style="margin-right: 8px; font-size: 14px; color: #e6a23c; font-weight: bold;">
                <el-icon><View /></el-icon> 管理员视角:
            </span>
            <el-dropdown @command="(cmd) => store.currentRole = cmd">
                <el-button type="warning" plain size="small">
                    {{ currentRole === 'teacher' ? '教师视角' : '学生视角' }}
                    <el-icon class="el-icon--right"><arrow-down /></el-icon>
                </el-button>
                <template #dropdown>
                    <el-dropdown-menu>
                        <el-dropdown-item command="teacher">👁️ 教师视角</el-dropdown-item>
                        <el-dropdown-item command="student">🎓 学生视角</el-dropdown-item>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
        </div>

        <!-- KB Management Button -->
        <el-button 
            v-if="currentRole === 'teacher' || store.realUserRole === 'internal_test'"
            type="primary" 
            :icon="Document" 
            @click="kbDrawerVisible = true"
            style="margin-right: 15px;"
        >
            知识库管理
        </el-button>

        <span style="margin-left: 15px;">
            <el-tag :type="store.realUserRole === 'internal_test' ? 'danger' : (currentRole === 'teacher' ? 'warning' : 'success')" effect="dark" style="margin-right: 5px;">
                {{ store.realUserRole === 'internal_test' ? '内测管理员' : (currentRole === 'teacher' ? '教师' : '学生') }}
            </el-tag>
            欢迎您，{{ store.currentUser?.name || (currentRole === 'teacher' ? '李老师' : '李同学') }}
        </span>
        <span style="margin-left: 10px; color: #ddd;">|</span>
        <el-button link type="danger" @click="store.logout" style="margin-left: 10px;">退出登录</el-button>
      </div>
    </div>
    
    <el-drawer
        v-model="kbDrawerVisible"
        title="知识库管理"
        direction="rtl"
        size="500px"
    >
        <KnowledgeBasePanel />
    </el-drawer>
    <div class="main-container">
      <slot></slot>
    </div>
    <div class="footer">
      © 2025 智能教学辅助系统 | 由生成式人工智能驱动
    </div>
  </div>
</template>

<style scoped>
/* Scoped styles if needed */
</style>
