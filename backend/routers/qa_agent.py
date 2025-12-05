from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest, ChatResponse
from services.rag_service import rag_service

router = APIRouter(prefix="/api", tags=["qa_agent"])

TEACHER_PERSONA = """你是一个新闻传播学领域的专业助教，服务对象是高校教师。
风格要求：
1. 专业、干练、客观，直击要点。
2. 分析式思维：提供多维度观点。
"""

STUDENT_PERSONA = """你是一个新闻传播学领域的智能学习伴侣，服务对象是高校学生。
风格要求：
1. 循循善诱、亲切、详尽。
2. 多用生活中的例子辅助解释。
3. 引导式思维：不仅给答案，还要引导学生思考，建立知识关联。
"""

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        context_str = ""
        sources = []
        
        # 1. Retrieve relevant documents (Only if use_kb is True)
        if request.use_kb:
            results = rag_service.retrieve(
                query=request.query, 
                user_id=request.user_id,
                role=request.role,
                target_user_ids=request.target_user_ids
            )
            
            documents = results['documents'][0]
            metadatas = results['metadatas'][0]
            
            context_parts = []
            for doc, meta in zip(documents, metadatas):
                source_name = meta.get('source', 'Unknown')
                context_parts.append(f"Source ({source_name}):\n{doc}")
                if source_name not in sources:
                    sources.append(source_name)
            
            context_str = "\n\n".join(context_parts)
        
        # 2. Select Persona based on Role
        base_persona = TEACHER_PERSONA if request.role == "teacher" else STUDENT_PERSONA
        
        # 3. Construct System Prompt based on KB usage
        if request.use_kb:
            system_prompt = base_persona + "\n请基于【背景知识】回答问题。必须严格引用来源，不要编造。"
        else:
            system_prompt = base_persona + "\n请基于你的专业知识进行回答。虽然没有提供特定背景材料，但请依然保持上述的专业风格。"
        
        # 4. Generate Answer
        answer = rag_service.generate_answer(
            query=request.query,
            context=context_str,
            history=request.history,
            system_prompt=system_prompt
        )
        
        return ChatResponse(answer=answer, sources=sources)

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
