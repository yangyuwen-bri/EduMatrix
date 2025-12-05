<script setup>
import { useAgentStore } from '../stores/agentStore'
import { storeToRefs } from 'pinia'

const store = useAgentStore()
const { quizData, studentAnswers } = storeToRefs(store)
</script>

<template>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h3>{{ quizData.title }}</h3>
        <div style="font-size: 14px; color: #666;">共 {{ quizData.questions.length }} 题</div>
    </div>

    <el-card v-for="(q, index) in quizData.questions" :key="q.id" style="margin-bottom: 15px;">
        <template #header>
            <div style="font-weight: bold;">第 {{ index + 1 }} 题</div>
        </template>
        <div style="font-size: 16px; margin-bottom: 15px;">{{ q.stem }}</div>
        <el-radio-group v-model="studentAnswers[q.id]" style="display: flex; flex-direction: column; align-items: flex-start;">
            <el-radio v-for="(opt, optIndex) in q.options" :key="optIndex" :label="String.fromCharCode(65+optIndex)" size="large" style="margin-bottom: 10px;">
                {{ String.fromCharCode(65+optIndex) }}. {{ opt }}
            </el-radio>
        </el-radio-group>
        
        <div v-if="studentAnswers[q.id]" style="margin-top: 15px; padding: 10px; background: #f0f9eb; border-radius: 4px;" :style="{ background: studentAnswers[q.id] === q.answer ? '#f0f9eb' : '#fef0f0' }">
            <div v-if="studentAnswers[q.id] === q.answer" style="color: #67c23a; font-weight: bold;">
                <el-icon><Select /></el-icon> 回答正确！
            </div>
            <div v-else style="color: #f56c6c; font-weight: bold;">
                <el-icon><Close /></el-icon> 回答错误。正确答案是 {{ q.answer }}
            </div>
            <div style="margin-top: 10px; color: #606266;">
                <strong>解析/提示：</strong>{{ q.analysis }}
            </div>
        </div>
    </el-card>
</template>
