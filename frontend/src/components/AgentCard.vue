<script setup>
import { computed } from 'vue'
import { useAgentStore } from '../stores/agentStore'
import { storeToRefs } from 'pinia'

const props = defineProps({
  agent: Object
})

const store = useAgentStore()
const { currentRole } = storeToRefs(store)

const isDisabled = computed(() => {
  return !props.agent.roles[currentRole.value]
})

const currentRoleConfig = computed(() => {
  return props.agent.roles[currentRole.value] || {}
})

const openAgent = () => {
  if (isDisabled.value) return
  store.currentAgent = props.agent.name
  store.dialogVisible = true
  // Initialize chat history or quiz data if needed
  store.chatHistory = []
  store.quizData = null
  
  // Welcome message logic
  let welcomeMsg = ''
  if (props.agent.name === '智能答疑助教') {
      welcomeMsg = currentRole.value === 'teacher'
          ? '老师您好！我是智能答疑助教。您可以模拟学生提问，来测试我的回答准确度。'
          : '同学你好！我是智能答疑助教。请问有什么关于新闻传播学的问题需要我解答吗？';
  } else if (props.agent.name === '智能出题助教') {
      welcomeMsg = currentRole.value === 'teacher'
          ? '老师您好！我是智能出题助教。请输入出题指令（如“出3道关于议程设置的选择题”），我将为您生成试卷。'
          : '同学你好！我是智能出题助教。请输入你想练习的知识点，我将为你出题并提供反馈。';
  } else if (props.agent.name === '智能批改助教') {
      welcomeMsg = currentRole.value === 'teacher'
          ? '老师您好！我是智能批改助教。您可以输入指令生成评分标准，在右侧编辑并批量上传学生作业进行批改。'
          : '同学你好！我是智能批改助教。请在右侧上传你的论文草稿，我将为你提供详细的诊断建议。';
  }

  if (welcomeMsg) {
      store.chatHistory = [{
          role: 'assistant',
          content: welcomeMsg
      }]
  }
}
</script>

<template>
  <el-card class="agent-card" :class="{ 'disabled-card': isDisabled }" shadow="hover" @click="openAgent">
    <template #header>
      <div class="card-header-custom">
        <span>{{ agent.name }}</span>
        <el-button v-if="!isDisabled" type="primary" size="small" round>
          {{ currentRoleConfig.actionText }}
        </el-button>
        <el-tag v-else type="info" size="small">无权限</el-tag>
      </div>
    </template>
    <div class="card-content">
      <el-tag size="small" :type="isDisabled ? 'info' : ''" class="feature-tag">{{ agent.tag }}</el-tag>
      <div class="desc-text">
        {{ isDisabled ? agent.baseFeature : currentRoleConfig.coreFunction }}
      </div>
      <div v-if="!isDisabled" class="highlight-box">
        特色: {{ agent.baseFeature.split('：')[1] }}
      </div>
    </div>
  </el-card>
</template>
