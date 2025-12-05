<script setup>
import { ref } from 'vue'
import { useAgentStore } from '../stores/agentStore'
import { storeToRefs } from 'pinia'

const loading = ref(false)
const useKB = ref(true)

const store = useAgentStore()
const { currentRole, quizData } = storeToRefs(store)
const activeNames = ref([])

const deleteQuestion = (index) => {
    if (quizData.value && quizData.value.questions) {
        quizData.value.questions.splice(index, 1);
    }
};

const exportQuiz = async () => {
    if (!quizData.value) return;
    
    try {
        const response = await fetch('/api/quiz/export', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(quizData.value) // Send the full quiz object directly
        });
        
        if (!response.ok) throw new Error('Export failed');
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'quiz.docx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
    } catch (e) {
        console.error(e);
        alert('导出失败，请检查后端日志');
    }
};
</script>

<template>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <el-input v-model="quizData.title" placeholder="试卷标题" style="font-size: 18px; font-weight: bold; width: 200px;"></el-input>
        <div style="font-size: 14px; color: #666;">共 {{ quizData.questions.length }} 题</div>
    </div>

    <div v-if="quizData.questions.length > 0">
        <el-collapse v-model="activeNames">
            <el-collapse-item v-for="(q, index) in quizData.questions" :key="q.id" :name="q.id">
                <template #title>
                    <div style="display: flex; justify-content: space-between; align-items: center; width: 100%; padding-right: 10px;">
                        <div style="font-weight: bold; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 80%;">
                            第 {{ index + 1 }} 题: {{ q.stem || '（空题干）' }}
                        </div>
                        <el-button type="danger" link icon="Delete" @click.stop="deleteQuestion(index)"></el-button>
                    </div>
                </template>
                
                <el-form label-position="top">
                    <el-form-item label="题干">
                        <el-input v-model="q.stem" type="textarea" :rows="2"></el-input>
                    </el-form-item>
                    <el-form-item label="难度">
                         <el-radio-group v-model="q.difficulty" size="small">
                            <el-radio-button label="easy">简单</el-radio-button>
                            <el-radio-button label="medium">中等</el-radio-button>
                            <el-radio-button label="hard">困难</el-radio-button>
                        </el-radio-group>
                    </el-form-item>
                    <el-form-item label="选项">
                        <div v-for="(opt, optIndex) in q.options" :key="optIndex" style="margin-bottom: 5px; display: flex; align-items: center;">
                            <span style="width: 30px; font-weight: bold;">{{ String.fromCharCode(65+optIndex) }}.</span>
                            <el-input v-model="q.options[optIndex]"></el-input>
                        </div>
                    </el-form-item>
                    <el-form-item label="正确答案">
                        <el-radio-group v-model="q.answer">
                            <el-radio v-for="(opt, optIndex) in q.options" :key="optIndex" :label="String.fromCharCode(65+optIndex)">{{ String.fromCharCode(65+optIndex) }}</el-radio>
                        </el-radio-group>
                    </el-form-item>
                    <el-form-item label="解析">
                        <el-input v-model="q.analysis" type="textarea" :rows="3" placeholder="请输入解析..."></el-input>
                    </el-form-item>
                </el-form>
            </el-collapse-item>
        </el-collapse>

        <div style="text-align: center; margin-top: 20px;">
            <el-button type="primary" size="large" icon="Download" @click="exportQuiz">导出试卷 (Word)</el-button>
        </div>
    </div>
    <el-empty v-else description="请在左侧对话框输入指令生成试卷"></el-empty>
</template>
