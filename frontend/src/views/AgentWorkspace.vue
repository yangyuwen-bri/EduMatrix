<script setup>
import { useAgentStore } from '../stores/agentStore'
import { storeToRefs } from 'pinia'
import ChatWindow from '../components/ChatWindow.vue'
import QuizEditor from '../components/QuizEditor.vue'
import QuizPlayer from '../components/QuizPlayer.vue'
import GradingPanel from '../components/GradingPanel.vue'

const store = useAgentStore()
const { currentAgent, currentRole, quizData } = storeToRefs(store)
</script>

<template>
  <div style="display: flex; height: 600px; gap: 20px;">
    <!-- Left Panel: Chat -->
    <div style="flex: 1; display: flex; flex-direction: column; border-right: 1px solid #eee; padding-right: 10px;">
      <ChatWindow />
    </div>

    <!-- Right Panel: Quiz Editor (Only for Quiz Agent) -->
    <div v-if="currentAgent === '智能出题助教' && quizData" style="flex: 1; padding-left: 10px; overflow-y: auto; display: flex; flex-direction: column;">
       <QuizEditor v-if="currentRole === 'teacher'" />
       <QuizPlayer v-else />
    </div>
    
    <!-- Right Panel: Grading Assistant -->
    <div v-else-if="currentAgent === '智能批改助教'" style="flex: 1; padding-left: 10px; overflow-y: auto; display: flex; flex-direction: column;">
        <GradingPanel />
    </div>
    
    <!-- Placeholder for other agents or empty state if no quizData -->
    <div v-else-if="currentAgent === '智能出题助教' && !quizData" style="flex: 1; padding-left: 10px; display: flex; align-items: center; justify-content: center; color: #999;">
        <el-empty description="请在左侧输入指令生成试卷"></el-empty>
    </div>
    
     <div v-else-if="currentAgent !== '智能出题助教' && currentAgent !== '智能答疑助教'" style="flex: 1; padding-left: 10px; display: flex; align-items: center; justify-content: center; color: #999;">
        <el-empty description="该功能模块正在开发中..."></el-empty>
    </div>
  </div>
</template>
