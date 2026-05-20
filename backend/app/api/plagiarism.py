from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.models.exam import Exam
from app.models.plagiarism import PlagiarismFlag
from app.models.extracted_answer import ExtractedAnswer
from app.models.submission import Submission
from gradeops_ai.evaluation.plagiarism_checker import check_plagiarism

router = APIRouter(prefix="/plagiarism", tags=["plagiarism"])

def run_plagiarism_background(exam_id: int, db: Session):
    exam = db.get(Exam, exam_id)
    if not exam:
        return
    
    # Get all extracted answers for this exam
    answers = db.query(ExtractedAnswer).join(Submission).filter(Submission.exam_id == exam_id).all()
    
    # Group by question_id
    grouped = {}
    for a in answers:
        grouped.setdefault(a.question_id, {})[a.submission_id] = a.answer_text
        
    for qid, sub_answers in grouped.items():
        if len(sub_answers) < 2:
            continue
            
        # Optional: fetch question text from rubric
        # For simplicity, pass generic
        matches = check_plagiarism(f"Question {qid}", sub_answers)
        for m in matches:
            flag = PlagiarismFlag(
                exam_id=exam_id,
                question_id=qid,
                submission_a_id=m.submission_a_id,
                submission_b_id=m.submission_b_id,
                explanation=m.explanation
            )
            db.add(flag)
    db.commit()

@router.post("/run/{exam_id}")
def trigger_plagiarism(
    exam_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.professor:
        return JSONResponse(status_code=403, content={"error": "Only professors can run plagiarism checks"})
    
    background_tasks.add_task(run_plagiarism_background, exam_id, db)
    return {"status": "processing"}

@router.get("/{exam_id}")
def get_plagiarism_flags(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    flags = db.query(PlagiarismFlag).filter(PlagiarismFlag.exam_id == exam_id).all()
    return [{"id": f.id, "question_id": f.question_id, "sub_a": f.submission_a_id, "sub_b": f.submission_b_id, "explanation": f.explanation} for f in flags]
