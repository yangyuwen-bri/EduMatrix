<script setup>
import { ref, computed } from 'vue'
import { useAgentStore } from '../stores/agentStore'
import { User, School, Key, Document, UploadFilled, ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const store = useAgentStore()
const dialogVisible = ref(true)
const internalTestKey = ref('')
const step = ref(1) // 1: Role, 2: KB Selection
const selectedRole = ref('')

// Step 1: Role Selection
const handleRoleSelect = (role) => {
  if (role === 'internal_test') {
    if (internalTestKey.value === 'test2025') { 
        store.currentUser = {
            id: 'internal_tester',
            role: 'internal_test',
            name: '内测管理员'
        }
        store.realUserRole = 'internal_test'
        store.currentRole = 'teacher' // Default view for internal tester
        ElMessage.success('内测模式登录成功 (默认教师视角)')
        dialogVisible.value = false
    } else {
        ElMessage.error('内测密钥错误')
    }
  } else {
    selectedRole.value = role
    step.value = 2
  }
}

const showInternalInput = ref(false)
const selectInternal = () => {
    showInternalInput.value = true
}
const confirmInternal = () => {
    handleRoleSelect('internal_test')
}

// Step 2: KB Selection
const uploadMode = ref(false)
const fileList = ref([])
const uploading = ref(false)

const handleDefaultKB = () => {
    const name = selectedRole.value === 'teacher' ? 'Teacher User' : 'Student User'
    store.login(selectedRole.value, name)
    dialogVisible.value = false
    ElMessage.success('已选择默认知识库')
}

const handleUploadKB = async () => {
    if (fileList.value.length === 0) {
        ElMessage.warning('请先选择文件')
        return
    }

    // We need a temporary ID to upload before "logging in", 
    // OR we generate the ID now, upload, then login.
    // Let's generate ID now.
    const tempId = Math.random().toString(36).substring(2, 15)
    
    uploading.value = true
    try {
        const formData = new FormData()
        formData.append('file', fileList.value[0].raw)
        formData.append('user_id', tempId)

        const response = await fetch('/api/kb/upload', {
            method: 'POST',
            body: formData
        })

        if (!response.ok) throw new Error('Upload failed')
        
        const data = await response.json()
        ElMessage.success('知识库上传成功')
        
        // Login with this ID
        const name = selectedRole.value === 'teacher' ? 'Teacher User' : 'Student User'
        store.loginWithId(selectedRole.value, name, tempId)
        dialogVisible.value = false
        
    } catch (e) {
        console.error(e)
        ElMessage.error('上传失败，请重试')
    } finally {
        uploading.value = false
    }
}

const goBack = () => {
    step.value = 1
    selectedRole.value = ''
    uploadMode.value = false
}

</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    :title="step === 1 ? '欢迎使用教学智能体' : '选择知识库'"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
    center
    class="login-modal"
  >
    <!-- Step 1: Role Selection -->
    <div v-if="step === 1" class="role-selection">
      <h3>请选择您的身份</h3>
      
      <div class="role-cards">
        <div class="role-card" @click="handleRoleSelect('teacher')">
          <el-icon :size="40"><School /></el-icon>
          <span>我是教师</span>
        </div>
        
        <div class="role-card" @click="handleRoleSelect('student')">
          <el-icon :size="40"><User /></el-icon>
          <span>我是学生</span>
        </div>

        <div class="role-card internal" @click="selectInternal" :class="{ active: showInternalInput }">
          <el-icon :size="40"><Key /></el-icon>
          <span>内部测试</span>
        </div>
      </div>

      <div v-if="showInternalInput" class="internal-input">
        <el-input 
            v-model="internalTestKey" 
            placeholder="请输入测试密钥 (默认为空)" 
            @keyup.enter="confirmInternal"
        >
            <template #append>
                <el-button @click="confirmInternal">进入</el-button>
            </template>
        </el-input>
      </div>
    </div>

    <!-- Step 2: KB Selection -->
    <div v-else class="kb-selection">
        <div class="back-btn" @click="goBack">
            <el-icon><ArrowLeft /></el-icon> 返回
        </div>

        <div v-if="!uploadMode" class="kb-options">
            <div class="kb-card" @click="handleDefaultKB">
                <el-icon :size="40"><Document /></el-icon>
                <span>使用默认知识库</span>
                <small>新闻传播学理论知识库</small>
            </div>
            
            <div class="kb-card upload" @click="uploadMode = true">
                <el-icon :size="40"><UploadFilled /></el-icon>
                <span>上传自定义知识库</span>
                <small>上传您的私有文档</small>
            </div>
        </div>

        <div v-else class="upload-ui">
            <h3>上传您的知识库文档</h3>
            <el-upload
                v-model:file-list="fileList"
                class="upload-demo"
                drag
                action="#"
                :auto-upload="false"
                :limit="1"
                :on-exceed="(files) => { fileList = [files[0]] }"
            >
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">
                    拖拽文件到此处或 <em>点击上传</em>
                </div>
            </el-upload>
            
            <div class="actions">
                <el-button @click="uploadMode = false">取消</el-button>
                <el-button type="primary" @click="handleUploadKB" :loading="uploading">
                    确认上传并进入
                </el-button>
            </div>
        </div>
    </div>
  </el-dialog>
</template>

<style scoped lang="scss">
.role-selection, .kb-selection {
  text-align: center;
  padding: 10px;
  position: relative;

  h3 {
    margin-bottom: 30px;
    color: #333;
  }
}

.back-btn {
    position: absolute;
    top: -40px;
    left: 0;
    cursor: pointer;
    display: flex;
    align-items: center;
    color: #666;
    &:hover { color: var(--el-color-primary); }
}

.role-cards, .kb-options {
  display: flex;
  justify-content: space-around;
  gap: 20px;
  margin-bottom: 20px;
}

.role-card, .kb-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 140px;
  height: 140px;
  border: 2px solid #eee;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #666;
  padding: 10px;

  &:hover {
    border-color: var(--el-color-primary);
    color: var(--el-color-primary);
    transform: translateY(-5px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  }

  &.internal {
    &:hover {
        border-color: #e6a23c;
        color: #e6a23c;
    }
    &.active {
        border-color: #e6a23c;
        color: #e6a23c;
    }
  }

  span {
    margin-top: 10px;
    font-weight: 500;
  }
  
  small {
      font-size: 12px;
      color: #999;
      margin-top: 5px;
  }
}

.internal-input, .upload-ui {
    margin-top: 20px;
    animation: fadeIn 0.3s ease;
}

.upload-ui {
    text-align: left;
    max-width: 400px;
    margin: 0 auto;
    
    h3 { text-align: center; }
    .actions {
        margin-top: 20px;
        text-align: center;
    }
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
