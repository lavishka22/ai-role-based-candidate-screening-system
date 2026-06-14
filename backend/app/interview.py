from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.session import InterviewSession, QuestionAnswer
from app.schemas.interview import StartSessionResponse, AnswerRequest, NextQuestionResponse, SummaryResponse
from app.services.resume_service import extract_text_from_upload, parse_resume, build_dynamic_queries
from app.services.rag_service import RAGService
from app.services.question_service import QuestionService

router = APIRouter(prefix="/api/interview", tags=["interview"])
rag = RAGService()
question_service = QuestionService()

@router.post("/start", response_model=StartSessionResponse)
async def start_interview(
    role: str = Form(...),
    resume: UploadFile = File(...),
    candidate_name: str | None = Form(None),
    db: Session = Depends(get_db),
):
    if not resume.filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Upload PDF or TXT resume only.")
    data = await resume.read()
    text = extract_text_from_upload(resume.filename, data)
    if len(text) < 50:
        raise HTTPException(status_code=400, detail="Resume text could not be extracted properly.")
    profile = parse_resume(text)
    session = InterviewSession(candidate_name=candidate_name, role=role, resume_text=text, extracted_profile=profile)
    db.add(session)
    db.commit()
    db.refresh(session)

    queries = build_dynamic_queries(role, profile)
    contexts = rag.retrieve(role, queries)
    q = question_service.generate_question(role, profile, contexts, [])
    qa = QuestionAnswer(
        session_id=session.id,
        question=q["question"],
        topic=q.get("topic"),
        difficulty=q.get("difficulty", "medium"),
        retrieved_context=q.get("trace", {}).get("used_context", ""),
    )
    db.add(qa)
    db.commit()
    db.refresh(qa)
    return {"session_id": session.id, "role": role, "extracted_profile": profile, "first_question": {"id": qa.id, **q}}

@router.post("/{session_id}/answer", response_model=NextQuestionResponse)
def answer_question(session_id: int, payload: AnswerRequest, db: Session = Depends(get_db)):
    session = db.get(InterviewSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    qa = db.get(QuestionAnswer, payload.question_id)
    if not qa or qa.session_id != session_id:
        raise HTTPException(status_code=404, detail="Question not found for this session.")
    qa.answer = payload.answer
    db.commit()

    history = [
        {"question": item.question, "answer": item.answer, "topic": item.topic}
        for item in session.qa_items
    ]
    if len(history) >= 5:
        return {"saved": True, "next_question": None}

    queries = build_dynamic_queries(session.role, session.extracted_profile)
    if payload.answer:
        queries.insert(0, f"Follow up technical question based on candidate answer: {payload.answer[:500]}")
    contexts = rag.retrieve(session.role, queries)
    q = question_service.generate_question(session.role, session.extracted_profile, contexts, history)
    new_qa = QuestionAnswer(
        session_id=session.id,
        question=q["question"],
        topic=q.get("topic"),
        difficulty=q.get("difficulty", "medium"),
        retrieved_context=q.get("trace", {}).get("used_context", ""),
    )
    db.add(new_qa)
    db.commit()
    db.refresh(new_qa)
    return {"saved": True, "next_question": {"id": new_qa.id, **q}}

@router.get("/{session_id}/summary", response_model=SummaryResponse)
def get_summary(session_id: int, db: Session = Depends(get_db)):
    session = db.get(InterviewSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    qa = [
        {"id": item.id, "question": item.question, "answer": item.answer, "topic": item.topic, "difficulty": item.difficulty}
        for item in session.qa_items
    ]
    summary = question_service.summarize(session.role, session.extracted_profile, qa)
    session.summary = summary
    db.commit()
    return {
        "session_id": session.id,
        "role": session.role,
        "extracted_profile": session.extracted_profile,
        "total_questions": len(qa),
        "qa": qa,
        "summary": summary,
    }
