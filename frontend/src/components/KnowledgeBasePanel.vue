<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAgentStore } from '../stores/agentStore'
import { storeToRefs } from 'pinia'
import { UploadFilled, Document, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const store = useAgentStore()
const { currentUser, realUserRole, targetUserIds } = storeToRefs(store)

const fileList = ref([])
const uploading = ref(false)
const remoteFiles = ref({}) // owner_id -> [filenames]
const loadingFiles = ref(false)

// For Admin Selection
const selectedUsers = ref([])

const isAdmin = computed(() => realUserRole.value === 'internal_test')

const fetchFiles = async () => {
    loadingFiles.value = true
    try {
        const formData = new FormData()
        if (currentUser.value) {
            formData.append('user_id', currentUser.value.id)
        }
        if (realUserRole.value) {
            formData.append('role', realUserRole.value)
        }

        const response = await fetch('/api/kb/list', {
            method: 'POST',
            body: formData
        })
        
        if (!response.ok) throw new Error('Fetch failed')
        
        const data = await response.json()
        remoteFiles.value = data.files
        
    } catch (e) {
        console.error(e)
        ElMessage.error('获取文件列表失败')
    } finally {
        loadingFiles.value = false
    }
}

const handleUpload = async () => {
    if (fileList.value.length === 0) {
        ElMessage.warning('请先选择文件')
        return
    }

    uploading.value = true
    try {
        const formData = new FormData()
        formData.append('file', fileList.value[0].raw)
        formData.append('user_id', currentUser.value.id)

        const response = await fetch('/api/kb/upload', {
            method: 'POST',
            body: formData
        })

        if (!response.ok) throw new Error('Upload failed')
        
        const data = await response.json()
        ElMessage.success(data.message)
        fileList.value = [] // Clear list
        fetchFiles() // Refresh list
        
    } catch (e) {
        console.error(e)
        ElMessage.error('上传失败，请重试')
    } finally {
        uploading.value = false
    }
}

// Watch selection changes to update store
import { watch } from 'vue'
watch(selectedUsers, (newVal) => {
    store.targetUserIds = newVal
})

onMounted(() => {
    fetchFiles()
})
</script>

<template>
    <div class="kb-panel">
        <div class="header">
            <h3>📚 {{ isAdmin ? '全局知识库管理 (管理员)' : '个人知识库管理' }}</h3>
            <p>{{ isAdmin ? '您可以查看所有用户上传的文档，并选择特定的知识库进行测试。' : '上传您的私有文档，AI 将基于这些文档回答您的问题。' }}</p>
        </div>

        <div class="upload-area">
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
                <template #tip>
                    <div class="el-upload__tip">
                        支持 PDF, Word, TXT 格式
                    </div>
                </template>
            </el-upload>
            
            <div class="actions">
                <el-button type="primary" size="large" @click="handleUpload" :loading="uploading">
                    上传到知识库
                </el-button>
            </div>
        </div>

        <div class="file-list-area">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h4>已上传文档</h4>
                <el-button :icon="Refresh" circle size="small" @click="fetchFiles" :loading="loadingFiles"></el-button>
            </div>
            
            <div v-if="loadingFiles" style="text-align: center; color: #999;">加载中...</div>
            
            <div v-else-if="Object.keys(remoteFiles).length === 0" style="text-align: center; color: #999;">
                暂无文档
            </div>

            <div v-else>
                <!-- Admin View: Group by User -->
                <div v-if="isAdmin">
                    <div style="margin-bottom: 10px; font-size: 12px; color: #666;">
                        <el-icon><InfoFilled /></el-icon> 勾选用户以指定 AI 使用其知识库（不勾选则默认使用全部）
                    </div>
                    <el-checkbox-group v-model="selectedUsers">
                        <div v-for="(files, owner) in remoteFiles" :key="owner" class="user-group">
                            <div class="user-header">
                                <el-checkbox :label="owner">
                                    <strong>{{ owner === 'system' ? '系统预置' : (owner === currentUser?.id ? '我上传的' : `用户 ${owner}`) }}</strong>
                                </el-checkbox>
                            </div>
                            <ul class="file-ul">
                                <li v-for="file in files" :key="file">
                                    <el-icon><Document /></el-icon> {{ file }}
                                </li>
                            </ul>
                        </div>
                    </el-checkbox-group>
                </div>

                <!-- Regular View: Simple List -->
                <div v-else>
                    <ul class="file-ul">
                        <template v-for="(files, owner) in remoteFiles" :key="owner">
                            <li v-for="file in files" :key="file">
                                <el-icon><Document /></el-icon> {{ file }}
                            </li>
                        </template>
                    </ul>
                </div>
            </div>
        </div>

        <div class="info-box" style="margin-top: 30px;">
            <el-alert
                title="隐私说明"
                type="info"
                :closable="false"
                show-icon
            >
                <p>您上传的文档仅对您自己可见（内部测试管理员除外）。</p>
            </el-alert>
        </div>
    </div>
</template>

<style scoped lang="scss">
.kb-panel {
    padding: 20px;
    height: 100%;
    overflow-y: auto;
}

.header {
    margin-bottom: 30px;
    text-align: center;
    
    h3 {
        margin-bottom: 10px;
        color: #333;
    }
    p {
        color: #666;
    }
}

.upload-area {
    max-width: 600px;
    margin: 0 auto 40px;
    
    .actions {
        margin-top: 20px;
        text-align: center;
    }
}

.file-list-area {
    max-width: 600px;
    margin: 0 auto;
    background: #fff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
}

.user-group {
    margin-bottom: 15px;
    border-bottom: 1px dashed #eee;
    padding-bottom: 10px;
    
    &:last-child {
        border-bottom: none;
    }
}

.file-ul {
    list-style: none;
    padding-left: 24px;
    margin-top: 5px;
    
    li {
        font-size: 13px;
        color: #666;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        gap: 5px;
    }
}

.info-box {
    max-width: 600px;
    margin: 0 auto;
}
</style>
