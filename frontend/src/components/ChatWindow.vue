<script setup>
import { ref, nextTick, watch, onMounted } from 'vue'
import { useAgentStore } from '../stores/agentStore'
import { storeToRefs } from 'pinia'
import { marked } from 'marked'
import mermaid from 'mermaid'

const store = useAgentStore()
const { chatHistory, loading, currentRole, currentAgent, quizData, currentRubric } = storeToRefs(store)
const inputMessage = ref('')
const chatContainer = ref(null)
const useKB = ref(true) // Default to true

onMounted(() => {
    mermaid.initialize({ startOnLoad: false });
})

const renderMarkdown = (text) => {
    if (!text) return '';
    let processedText = text.replace(/```mermaid([\s\S]*?)```/g, '<div class="mermaid">$1</div>');
    return marked.parse(processedText);
};

const renderMermaid = async () => {
    await nextTick();
    try {
        await mermaid.run({
            querySelector: '.mermaid'
        });
    } catch (e) {
        console.error('Mermaid rendering error:', e);
    }
};

const getPlaceholder = () => {
    if (currentAgent.value === '智能出题助教') {
        return currentRole.value === 'teacher' 
            ? '请输入出题指令（如：出3道关于议程设置的选择题）' 
            : '请输入你想练习的知识点（如：出3道关于议程设置的题）';
    } else if (currentAgent.value === '智能批改助教') {
        return currentRole.value === 'teacher'
            ? '请输入评分标准要求（如：生成一份关于新闻评论的评分标准）'
            : '请直接在右侧上传论文草稿进行智能诊断';
    }
    return '请输入你的问题...';
};

const sendMessage = async () => {
    if (!inputMessage.value.trim()) return;

    const query = inputMessage.value;
    chatHistory.value.push({
        role: 'user',
        content: query
    });
    inputMessage.value = '';
    loading.value = true;

    try {
        let endpoint = '/api/chat';
        if (currentAgent.value === '智能出题助教') {
            endpoint = '/api/quiz/generate';
            if (!quizData.value) {
                quizData.value = { title: "我的试卷", questions: [] };
            }
        } else if (currentAgent.value === '智能批改助教') {
            endpoint = '/api/grading/rubric';
        }
        
        const response = await fetch(endpoint, { // Proxy handles host
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                history: chatHistory.value.map(msg => ({ role: msg.role, content: msg.content })),
                role: currentRole.value,
                user_id: store.currentUser?.id, // Pass user_id for KB isolation
                use_kb: useKB.value,
                target_user_ids: store.targetUserIds // Pass selected users for admin filter
            })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        if (endpoint === '/api/quiz/generate') {
            if (data.questions && data.questions.length > 0) {
                const startId = quizData.value.questions.length + 1;
                const newQuestions = data.questions.map((q, i) => ({
                    ...q,
                    id: startId + i
                 }));
                quizData.value.questions.push(...newQuestions);
                
                chatHistory.value.push({
                    role: 'assistant',
                    content: `已为您生成 ${newQuestions.length} 道新题，请在右侧查看。`
                });
            } else {
                chatHistory.value.push({
                    role: 'assistant',
                    content: '未能生成有效题目，请尝试更换指令。'
                });
            }
        } else if (endpoint === '/api/grading/rubric') {
            // Hybrid Response Handling
            if (data.rubric) {
                currentRubric.value = data.rubric;
            }
            chatHistory.value.push({
                role: 'assistant',
                content: data.message || (data.rubric ? `已为您生成评分标准【${data.rubric.title}】，请在右侧查看。` : '收到。')
            });
        } else {
            chatHistory.value.push({
                role: 'assistant',
                content: data.answer,
                sources: data.sources
            });
            renderMermaid();
        }

    } catch (error) {
        console.error('Error:', error);
        chatHistory.value.push({
            role: 'assistant',
            content: '抱歉，系统暂时出现故障，请检查后端服务是否启动或 API Key 是否配置。'
        });
    } finally {
        loading.value = false;
        setTimeout(() => {
            if (chatContainer.value) {
                chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
            }
        }, 100);
    }
};
</script>

<template>
    <div style="flex: 1; display: flex; flex-direction: column; height: 100%;">
        <div ref="chatContainer"
            style="flex: 1; overflow-y: auto; padding: 20px; background: #f9f9f9; border-radius: 8px; margin-bottom: 20px;">
            <div v-for="(msg, index) in chatHistory" :key="index"
                :class="['chat-message-row', msg.role === 'user' ? 'user-message' : 'agent-message']">
                <div v-if="msg.role === 'assistant'" class="avatar-container">
                    <div class="avatar-circle">AI</div>
                </div>
                <div class="chat-bubble">
                    <div class="chat-content" v-html="renderMarkdown(msg.content)"></div>
                    <div v-if="msg.sources && msg.sources.length > 0" class="chat-source">
                        参考来源: {{ msg.sources.join(', ') }}
                    </div>
                </div>
                <div v-if="msg.role === 'user'" class="avatar-container">
                    <div class="avatar-circle user-avatar">我</div>
                </div>
            </div>
            <div v-if="loading" style="text-align: center; color: #999; margin-top: 10px;">
                <el-icon class="is-loading">
                    <Loading />
                </el-icon> 正在思考中...
            </div>
        </div>

        <div class="input-area">
      <div class="toolbar">
        <el-switch
            v-model="useKB"
            active-text="结合知识库"
            inactive-text="仅使用大模型"
            inline-prompt
            style="--el-switch-on-color: #13ce66; margin-bottom: 10px;"
        />
      </div>
      <div class="input-box">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="3"
          placeholder="请输入您的问题..."
          @keyup.enter.ctrl="sendMessage"
        />
        <el-button type="primary" :loading="loading" @click="sendMessage">发送</el-button>
      </div>
    </div>
    </div>
</template>
