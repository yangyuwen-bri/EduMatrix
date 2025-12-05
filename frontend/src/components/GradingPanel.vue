<script setup>
import { ref, computed } from 'vue'
import { useAgentStore } from '../stores/agentStore'
import { storeToRefs } from 'pinia'
import { ElMessage } from 'element-plus'

const store = useAgentStore()
const { currentRubric, gradingResults, currentRole } = storeToRefs(store)
const fileList = ref([])
const uploading = ref(false)
const rubric = ref(null)
const loading = ref(false)
const activeTab = ref('rubric')
const useKB = ref(true)
const rubricTopic = ref('')

const totalWeight = computed(() => {
    if (!currentRubric.value) return 0;
    return currentRubric.value.items.reduce((sum, item) => sum + item.weight, 0);
})

const handleRemoveItem = (index) => {
    currentRubric.value.items.splice(index, 1);
}

const handleAddItem = () => {
    currentRubric.value.items.push({
        criterion: "新维度",
        weight: 10,
        description: "请输入评分细则"
    });
}

const startGrading = async () => {
    if (fileList.value.length === 0) {
        ElMessage.warning('请先上传学生作业文件');
        return;
    }
    
    uploading.value = true;
    const formData = new FormData();
    if (currentRubric.value) {
        formData.append('rubric', JSON.stringify(currentRubric.value));
    }
    
    fileList.value.forEach(file => {
        formData.append('files', file.raw);
    });
    
    try {
        const response = await fetch('/api/grading/batch', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error('Grading failed');
        
        const data = await response.json();
        gradingResults.value = data;
        ElMessage.success('批量批改完成！');

        // Inject context into chat history
        if (data.results && data.results.length > 0) {
            const result = data.results[0]; // Take the first one for context if multiple
            const contextMsg = `【系统通知】用户已上传文件 ${result.filename}。
文章内容摘要：
${result.extracted_text || '（内容未提取）'}...

AI 诊断结果：
${result.feedback}`;
            
            // Push to chat history as a hidden system context or just a user message simulation
            // To make it natural, we can add it as a user message saying "I uploaded..." or just let the agent know.
            // But since we want the *Agent* to know it for the *next* turn, we just push it to the store.
            // We can mark it as 'system' role if backend supports it, or just 'user' to simulate.
            // Let's use 'user' to simulate "Here is my paper".
            store.chatHistory.push({
                role: 'user',
                content: `我上传了文件【${result.filename}】，内容如下：\n${result.extracted_text}\n\n请根据以上内容和你的诊断结果回答我的后续问题。`
            });
            
            // Also push the assistant's response (the feedback) so the conversation flow is complete
            store.chatHistory.push({
                role: 'assistant',
                content: `收到。我已对【${result.filename}】完成了诊断。总体评价：${result.feedback}。请问您有什么具体问题？`
            });
        }
        
    } catch (e) {
        console.error(e);
        ElMessage.error('批改失败，请检查后端日志');
    } finally {
        uploading.value = false;
    }
}

const reset = () => {
    gradingResults.value = null;
    fileList.value = [];
}

const reGradeItem = async (row, index) => {
    // Find the original file
    // Note: row.filename is now available from backend
    const file = fileList.value.find(f => f.name === row.filename);
    
    if (!file) {
        ElMessage.error('找不到原始文件，无法重新评估');
        return;
    }

    // Set loading state for this row (we need to make row reactive or use a separate loading state)
    // Since gradingResults is from store, it's reactive. We can add a temporary property.
    row.loading = true;

    const formData = new FormData();
    if (currentRubric.value) {
        formData.append('rubric', JSON.stringify(currentRubric.value));
    }
    formData.append('files', file.raw);

    try {
        const response = await fetch('/api/grading/batch', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error('Re-grading failed');
        
        const data = await response.json();
        // data.results contains the new result (list of 1)
        if (data.results && data.results.length > 0) {
            // Update the row in place
            const newResult = data.results[0];
            // We update properties one by one to keep the object reference if needed, or just replace
            // Replacing in the array is safer for reactivity
            gradingResults.value.results[index] = { ...newResult, loading: false };
            
            // Recalculate average
            const total = gradingResults.value.results.reduce((sum, r) => sum + r.total_score, 0);
            gradingResults.value.average_score = total / gradingResults.value.results.length;
            
            ElMessage.success('重新评估完成');
        }
        
    } catch (e) {
        console.error(e);
        ElMessage.error('重新评估失败');
        row.loading = false;
    }
}
</script>

<template>
    <div v-if="currentRole === 'teacher' && !currentRubric" style="display: flex; justify-content: center; align-items: center; height: 100%; color: #999;">
        <el-empty description="请在左侧对话框输入指令生成评分标准"></el-empty>
    </div>

    <div v-else-if="!gradingResults" class="rubric-designer">
        <!-- Teacher: Rubric Editor -->
        <div v-if="currentRole === 'teacher'">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3>{{ currentRubric.title }} (总权重: {{ totalWeight }}%)</h3>
                <el-button type="primary" @click="handleAddItem" size="small">添加维度</el-button>
            </div>



            <el-collapse>
                <el-collapse-item v-for="(item, index) in currentRubric.items" :key="index" :name="index">
                    <template #title>
                        <div style="display: flex; justify-content: space-between; width: 100%; padding-right: 10px;">
                            <span>{{ item.criterion }} ({{ item.weight }}%)</span>
                            <el-button type="danger" link icon="Delete" @click.stop="handleRemoveItem(index)"></el-button>
                        </div>
                    </template>
                    <el-form label-position="top">
                        <el-row :gutter="20">
                            <el-col :span="16">
                                <el-form-item label="维度名称">
                                    <el-input v-model="item.criterion"></el-input>
                                </el-form-item>
                            </el-col>
                            <el-col :span="8">
                                 <el-form-item label="权重">
                                    <el-input-number v-model="item.weight" :min="0" :max="100"></el-input-number>
                                </el-form-item>
                            </el-col>
                        </el-row>
                        <el-form-item label="评分细则">
                            <el-input v-model="item.description" type="textarea" :rows="2"></el-input>
                        </el-form-item>
                    </el-form>
                </el-collapse-item>
            </el-collapse>
        </div>
        
        <!-- Student: Self-Check Intro -->
        <div v-else style="margin-bottom: 20px; padding: 20px; background: #f0f9eb; border-radius: 8px;">
            <h3>🎓 论文自查模式</h3>
            <p>直接上传您的论文草稿，AI 将从论点、论据、逻辑、规范等方面进行诊断并给出修改建议。</p>
        </div>

        <div style="margin-top: 30px; border-top: 1px dashed #eee; padding-top: 20px;">
            <h4>{{ currentRole === 'teacher' ? '批量批改 (支持 PDF/Word)' : '上传论文草稿 (支持 PDF/Word)' }}</h4>
            <el-upload
                v-model:file-list="fileList"
                class="upload-demo"
                drag
                action="#"
                multiple
                :auto-upload="false"
            >
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">
                    拖拽文件到此处或 <em>点击上传</em>
                </div>
            </el-upload>
            
            <div style="text-align: center; margin-top: 20px;">
                <el-button type="success" size="large" @click="startGrading" :loading="uploading">
                    {{ uploading ? '正在智能诊断中...' : (currentRole === 'teacher' ? '开始批量批改' : '开始智能诊断') }}
                </el-button>
            </div>
        </div>
    </div>

    <div v-else class="grading-results">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h3>{{ currentRole === 'teacher' ? `批改结果 (平均分: ${gradingResults.average_score.toFixed(1)})` : '诊断报告' }}</h3>
            <el-button @click="reset">重新批改</el-button>
        </div>
        
        <el-table :data="gradingResults.results" style="width: 100%">
            <el-table-column type="expand">
                <template #default="props">
                    <div style="padding: 20px; background: #f9f9f9;">
                        <p><strong>总体评价：</strong> {{ props.row.feedback }}</p>
                        <div v-for="(score, criterion) in props.row.details" :key="criterion">
                            <strong>{{ criterion }}:</strong> {{ score }} {{ currentRole === 'teacher' ? '分' : '' }}
                        </div>
                    </div>
                </template>
            </el-table-column>
            <el-table-column label="学生/文件名" prop="student_name" />
            <el-table-column v-if="currentRole === 'teacher'" label="总分" prop="total_score" sortable>
                <template #default="scope">
                    <el-tag :type="scope.row.total_score >= 60 ? 'success' : 'danger'">{{ scope.row.total_score }}</el-tag>
                </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
                <template #default="scope">
                    <el-button size="small" type="primary" link @click="reGradeItem(scope.row, scope.$index)" :loading="scope.row.loading">
                        {{ currentRole === 'teacher' ? '重新评估' : '重新诊断' }}
                    </el-button>
                </template>
            </el-table-column>
        </el-table>
    </div>
</template>
