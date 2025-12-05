<script setup>
import Layout from './components/Layout.vue'
import Dashboard from './views/Dashboard.vue'
import AgentWorkspace from './views/AgentWorkspace.vue'
import LoginModal from './components/LoginModal.vue'
import { useAgentStore } from './stores/agentStore'
import { storeToRefs } from 'pinia'

const store = useAgentStore()
const { dialogVisible, currentAgent, currentUser } = storeToRefs(store)
const { handleClose } = store
</script>

<template>
  <Layout>
    <Dashboard />
  </Layout>
  
  <el-dialog v-model="dialogVisible" :title="currentAgent + ' - 运行中'" width="90%" :before-close="handleClose" destroy-on-close>
      <AgentWorkspace />
  </el-dialog>

  <LoginModal v-if="!currentUser" />
</template>

<style>
/* Import global styles */
@import './style.scss';
</style>
