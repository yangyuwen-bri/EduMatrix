<script setup>
import AgentCard from '../components/AgentCard.vue'
import { useAgentStore } from '../stores/agentStore'
import { storeToRefs } from 'pinia'

const store = useAgentStore()
const { agents, currentRole } = storeToRefs(store)
</script>

<template>
  <div class="dashboard">
    <div class="section-title">
      智能体功能模块 ({{ currentRole === 'teacher' ? '教师端' : '学生端' }})
    </div>
    <el-row :gutter="20">
      <el-col :span="8" v-for="agent in agents" :key="agent.name" style="margin-bottom: 20px;">
        <AgentCard :agent="agent" />
      </el-col>
    </el-row>
  </div>
</template>
