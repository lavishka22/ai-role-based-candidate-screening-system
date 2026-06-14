from pydantic import BaseModel

class StartSessionResponse(BaseModel):
    session_id: int
    role: str
    extracted_profile: dict
    first_question: dict

class AnswerRequest(BaseModel):
    question_id: int
    answer: str

class NextQuestionResponse(BaseModel):
    saved: bool
    next_question: dict | None = None

class SummaryResponse(BaseModel):
    session_id: int
    role: str
    extracted_profile: dict
    total_questions: int
    qa: list[dict]
    summary: str
