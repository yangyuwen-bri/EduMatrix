from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from models.schemas import ChatRequest, Rubric, RubricItem, GradingResult, GradingReport, RubricGenerationResponse
from services.rag_service import rag_service
import json
from typing import List
import pypdf
import docx
import io

router = APIRouter(prefix="/api/grading", tags=["grading_agent"])

RUBRIC_PERSONA = """你是一个专业的教育评估专家。
要求：
1. **混合输出模式**：
   - 如果用户只是咨询或闲聊，请直接用纯文本回答。
   - 如果用户要求生成或修改评分标准，请将 JSON 数据包裹在 `<RUBRIC_JSON>` 和 `</RUBRIC_JSON>` 标签中，并在标签外提供简要说明。

2. **JSON 结构（必须在标签内）**：
{
  "title": "评分标准标题",
  "items": [
    {
      "criterion": "维度名称",
      "weight": 30,
      "description": "评分细则..."
    }
  ]
}
3. 包含 3-5 个评分维度，总权重必须为 100。
"""

GRADING_PROMPT_TEMPLATE = """你是一个公正的阅卷老师。
请根据以下【评分标准】对【学生作业】进行评分。

【评分标准】：
{rubric_json}

【学生作业】：
{student_text}

要求：
1. 返回严格的 JSON 格式。
2. 对每个维度打分，并计算总分。
3. 提供总体评语（feedback）。
4. JSON 结构如下：
{{
  "student_name": "Unknown", 
  "total_score": 85,
  "feedback": "总体评价...",
  "details": {{
    "维度1": 25,
    "维度2": 30
  }}
}}
5. **只返回 JSON 字符串**。
"""

@router.post("/rubric", response_model=RubricGenerationResponse)
async def generate_rubric(request: ChatRequest):
    try:
        context_str = ""
        
        # 1. Retrieve relevant documents (Only if use_kb is True)
        if request.use_kb:
            # For rubric generation, we might want to retrieve curriculum standards
            results = rag_service.retrieve(request.query, role=request.role, target_user_ids=request.target_user_ids)
            if results['documents']:
                context_str = "\n".join(results['documents'][0])
        
        # 2. Construct Prompt
        if request.use_kb and context_str:
            prompt = RUBRIC_PERSONA + f"\n请根据用户的要求和以下【参考资料】，为【{request.query}】生成或优化评分标准。\n\n【参考资料】：\n{context_str}"
        else:
            prompt = RUBRIC_PERSONA + f"\n请根据用户的要求，为【{request.query}】生成或优化评分标准。"
        
        # Call LLM
        response_text = rag_service.generate_answer(
            query=request.query,
            context="", # Context is already embedded in prompt
            history=request.history,
            system_prompt=prompt
        )
        
        # Parse Hybrid Output
        rubric_data = None
        message = response_text
        
        import re
        json_match = re.search(r'<RUBRIC_JSON>(.*?)</RUBRIC_JSON>', response_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1).strip()
            # Clean potential markdown inside tags
            if json_str.startswith("```json"):
                json_str = json_str.replace("```json", "").replace("```", "")
            elif json_str.startswith("```"):
                json_str = json_str.replace("```", "")
            
            try:
                data = json.loads(json_str)
                rubric_data = Rubric(**data)
                # Remove the JSON part from the message to avoid clutter, or keep it?
                # Let's keep the message clean, remove the tags and content
                message = re.sub(r'<RUBRIC_JSON>.*?</RUBRIC_JSON>', '', response_text, flags=re.DOTALL).strip()
                if not message:
                    message = "已为您生成评分标准，请在右侧查看。"
            except json.JSONDecodeError:
                print(f"JSON Decode Error in Rubric: {json_str}")
                # Fallback: return text only with error hint?
                pass

        return RubricGenerationResponse(message=message, rubric=rubric_data)
        
    except Exception as e:
        print(f"Rubric Generation Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch", response_model=GradingReport)
async def batch_grade(
    files: List[UploadFile] = File(...),
    rubric: str = Form(None)
):
    results = []
    total_score_sum = 0
    
    # Default Rubric/Prompt for Student Self-Check
    DEFAULT_STUDENT_PROMPT = """你是一个学术写作指导老师。
请对以下【学生论文草稿】进行诊断。
不需要打分，请重点从以下几个方面进行定性评价并给出修改建议：
1. 论点清晰度 (Thesis Clarity)
2. 论据充分性 (Evidence & Argumentation)
3. 逻辑结构 (Logical Structure)
4. 学术规范 (Academic Integrity)

【学生论文草稿】：
{student_text}

要求：
1. 返回严格的 JSON 格式。
2. JSON 结构如下：
{{
  "student_name": "Unknown", 
  "total_score": 0,
  "feedback": "总体评价...",
  "details": {{
    "论点": "评价...",
    "论据": "评价...",
    "逻辑": "评价...",
    "规范": "评价..."
  }}
}}
3. **只返回 JSON 字符串**。
"""
    
    try:
        rubric_json_str = ""
        if rubric:
            rubric_obj = json.loads(rubric)
            rubric_json_str = json.dumps(rubric_obj, ensure_ascii=False)
        
        for file in files:
            content = ""
            filename = file.filename
            
            # Parse File
            if filename.endswith(".pdf"):
                pdf_reader = pypdf.PdfReader(file.file)
                for page in pdf_reader.pages:
                    content += page.extract_text()
            elif filename.endswith(".docx"):
                doc = docx.Document(file.file)
                for para in doc.paragraphs:
                    content += para.text + "\n"
            else:
                content = (await file.read()).decode("utf-8")
                
            # Grade
            if rubric:
                prompt = GRADING_PROMPT_TEMPLATE.format(
                    rubric_json=rubric_json_str,
                    student_text=content[:3000]
                )
            else:
                prompt = DEFAULT_STUDENT_PROMPT.format(
                    student_text=content[:3000]
                )
            
            json_str = rag_service.generate_answer(
                query="Grade this essay",
                context="",
                history=[],
                system_prompt=prompt
            )
            
            # Clean JSON
            if json_str.startswith("```json"):
                json_str = json_str.replace("```json", "").replace("```", "")
            elif json_str.startswith("```"):
                json_str = json_str.replace("```", "")
            
            try:
                grade_data = json.loads(json_str)
                # Ensure student name uses filename if not detected
                if grade_data.get("student_name") == "Unknown":
                    grade_data["student_name"] = filename
                
                result = GradingResult(**grade_data, filename=filename, extracted_text=content[:2000])
                results.append(result)
                total_score_sum += result.total_score
            except Exception as e:
                print(f"Error grading {filename}: {e}")
                results.append(GradingResult(
                    student_name=filename,
                    filename=filename,
                    total_score=0,
                    feedback=f"Error: {str(e)}",
                    details={}
                ))

        average = total_score_sum / len(results) if results else 0
        return GradingReport(results=results, average_score=average)

    except Exception as e:
        print(f"Batch Grading Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
