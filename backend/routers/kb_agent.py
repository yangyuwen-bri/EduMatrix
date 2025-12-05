from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from services.rag_service import rag_service
import pypdf
import docx

router = APIRouter(prefix="/api/kb", tags=["kb_agent"])

@router.post("/upload")
async def upload_to_kb(
    file: UploadFile = File(...),
    user_id: str = Form(...)
):
    try:
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
            
        if not content.strip():
            raise HTTPException(status_code=400, detail="File is empty or could not be read")
            
        # Add to Chroma
        num_chunks = rag_service.add_document(content, filename, user_id)
        
        return {"status": "success", "message": f"Successfully added {filename} ({num_chunks} chunks) to Knowledge Base"}
        
    except Exception as e:
        print(f"KB Upload Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list")
async def list_files(
    user_id: str = Form(None),
    role: str = Form(None)
):
    try:
        files_map = rag_service.list_documents(user_id, role)
        return {"files": files_map}
    except Exception as e:
        print(f"KB List Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
