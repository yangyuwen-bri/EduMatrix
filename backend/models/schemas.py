from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    query: str
    history: Optional[List[dict]] = [] # List of {"role": "user"/"assistant", "content": "..."}
    role: Optional[str] = "student" # "student" or "teacher"
    user_id: Optional[str] = None # User ID for KB isolation
    use_kb: bool = True # Whether to use Knowledge Base
    target_user_ids: Optional[List[str]] = None # For internal_test admin to filter KBs

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]

class QuizQuestion(BaseModel):
    id: int
    type: str = "single_choice"
    stem: str
    options: List[str] = []
    answer: str
    analysis: str
    difficulty: str = "medium"

class QuizResponse(BaseModel):
    title: str
    questions: List[QuizQuestion]
    sources: Optional[List[str]] = []

class QuizGenerationResponse(BaseModel):
    questions: List[QuizQuestion]
    sources: List[str]

class RubricItem(BaseModel):
    criterion: str
    weight: int
    description: str

class Rubric(BaseModel):
    title: str
    items: List[RubricItem]

class RubricGenerationResponse(BaseModel):
    message: str
    rubric: Optional[Rubric] = None

class GradingResult(BaseModel):
    student_name: str
    filename: str
    total_score: float
    feedback: str
    details: dict # criterion -> score
    extracted_text: Optional[str] = None

class GradingReport(BaseModel):
    results: List[GradingResult]
    average_score: float
