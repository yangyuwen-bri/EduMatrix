import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAgentStore = defineStore('agent', () => {
    const currentRole = ref('teacher')
    const realUserRole = ref(null) // Track the actual logged-in role
    const currentAgent = ref('')
    const chatHistory = ref([])
    const quizData = ref(null)
    const studentAnswers = ref({})
    const currentRubric = ref(null)
    const gradingResults = ref(null)
    const loading = ref(false)
    const dialogVisible = ref(false)

    // User State
    const currentUser = ref(null) // { id, role, name }
    const targetUserIds = ref([]) // For internal_test admin to filter KBs

    const login = (role, name) => {
        // Generate a random ID for this session if not exists
        const id = Math.random().toString(36).substring(2, 15)
        currentUser.value = {
            id,
            role,
            name
        }
        currentRole.value = role
        realUserRole.value = role
    }

    const loginWithId = (role, name, id) => {
        currentUser.value = {
            id,
            role,
            name
        }
        currentRole.value = role
        realUserRole.value = role
    }

    const logout = () => {
        currentUser.value = null
        currentRole.value = 'teacher'
        realUserRole.value = null
        resetState()
    }

    const agents = ref([
        {
            name: "智能答疑助教",
            tag: "交互",
            baseFeature: "核心功能：7x24小时即时响应提问，支持多轮对话深度解答。",
            roles: {
                teacher: {
                    coreFunction: "模拟学生提问，测试知识库覆盖度与回答准确性。",
                    actionText: "进入测试"
                },
                student: {
                    coreFunction: "解答课程疑问，提供相关知识点解析。",
                    actionText: "开始提问"
                },
                internal_test: {
                    coreFunction: "【全库检索】测试知识库覆盖度与回答准确性。",
                    actionText: "系统测试"
                }
            }
        },
        {
            name: "智能出题助教",
            tag: "工具",
            baseFeature: "核心功能：根据知识点自动生成试题，支持多种题型。",
            roles: {
                teacher: {
                    coreFunction: "快速生成试卷，支持编辑和导出。",
                    actionText: "生成试卷"
                },
                student: {
                    coreFunction: "自测练习，即时反馈。",
                    actionText: "开始练习"
                },
                internal_test: {
                    coreFunction: "测试试题生成逻辑与导出功能。",
                    actionText: "功能测试"
                }
            }
        },
        {
            name: "智能批改助教",
            tag: "反馈",
            baseFeature: "增量反馈机制：指出错误并提供改进思路和参考文献。",
            roles: {
                teacher: {
                    coreFunction: "批量批改学生作业，提供详细修改建议和评分。",
                    actionText: "批量批改"
                },
                student: {
                    coreFunction: "上传作业草稿，获取AI预评分和修改建议。",
                    actionText: "作业自查"
                },
                internal_test: {
                    coreFunction: "测试评分标准生成与批改准确性。",
                    actionText: "算法测试"
                }
            }
        },
        {
            name: "课件生成助教",
            tag: "工具",
            baseFeature: "核心功能：根据知识点自动生成PPT大纲，智能配图和案例匹配。",
            roles: {
                teacher: {
                    coreFunction: "快速生成课件大纲，辅助备课。",
                    actionText: "生成课件"
                },
                internal_test: {
                    coreFunction: "测试课件生成逻辑。",
                    actionText: "功能测试"
                }
            }
        },
        {
            name: "课程思政助教",
            tag: "育人",
            baseFeature: "核心功能：挖掘课程中的思政元素，匹配典型案例。",
            roles: {
                teacher: {
                    coreFunction: "提供思政融入点建议，生成教学设计。",
                    actionText: "获取建议"
                },
                internal_test: {
                    coreFunction: "测试思政元素匹配算法。",
                    actionText: "算法测试"
                }
            }
        },
        {
            name: "学情分析助教",
            tag: "数据",
            baseFeature: "能力画像：建立理论掌握度、批判思维、实践应用三维能力模型。",
            roles: {
                teacher: {
                    coreFunction: "分析全班学习行为数据，诊断整体知识薄弱点。",
                    actionText: "查看报告"
                },
                internal_test: {
                    coreFunction: "测试数据分析模型。",
                    actionText: "模型测试"
                }
            }
        },
        {
            name: "前沿资讯助教",
            tag: "拓展",
            baseFeature: "热点追踪：捕捉传媒业重大事件，引导学生用课程理论进行解读。",
            roles: {
                teacher: {
                    coreFunction: "获取最新学术前沿和行业动态，辅助备课。",
                    actionText: "获取资讯"
                },
                student: {
                    coreFunction: "阅读精选行业动态，拓展专业视野。",
                    actionText: "查看资讯"
                },
                internal_test: {
                    coreFunction: "测试资讯抓取与推荐逻辑。",
                    actionText: "功能测试"
                }
            }
        },
        {
            name: "视频讲解助教",
            tag: "资源",
            baseFeature: "碎片化设计：将长知识点拆解为5-8分钟短视频。",
            roles: {
                teacher: {
                    coreFunction: "生成知识点讲解脚本，配合字幕和关键帧标注。",
                    actionText: "制作微课"
                },
                internal_test: {
                    coreFunction: "测试脚本生成与视频合成逻辑。",
                    actionText: "功能测试"
                }
            }
        },
        {
            name: "就业指导助教",
            tag: "生涯",
            baseFeature: "人岗匹配：分析简历与岗位JD的匹配度，提供优化建议。",
            roles: {
                student: {
                    coreFunction: "模拟面试，优化简历，推荐实习岗位。",
                    actionText: "模拟面试"
                },
                internal_test: {
                    coreFunction: "测试人岗匹配算法。",
                    actionText: "算法测试"
                }
            }
        }
    ])

    const resetState = () => {
        chatHistory.value = []
        quizData.value = null
        studentAnswers.value = {}
        currentRubric.value = null
        gradingResults.value = null
        loading.value = false
    }

    const handleClose = (done) => {
        dialogVisible.value = false
        resetState()
        if (done && typeof done === 'function') done()
    }

    return {
        currentRole,
        realUserRole,
        currentAgent,
        chatHistory,
        quizData,
        studentAnswers,
        currentRubric,
        gradingResults,
        loading,
        dialogVisible,
        agents,
        handleClose,

        resetState,
        currentUser,
        login,
        loginWithId,
        login,
        loginWithId,
        logout,
        targetUserIds
    }
})
