import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.models.evaluation import Evaluation, EvaluationStatus
from app.models.extracted_answer import ExtractedAnswer
from app.models.rubric import Rubric
from app.models.submission import Submission


def save_extracted_answers(
    db: Session, submission_id: str, answers: dict[str, str]
) -> None:
    """Persist OCR/extracted answers. AI Pipeline Engineer calls after OCR."""
    sub_uuid = uuid.UUID(submission_id)
    submission = db.get(Submission, sub_uuid)
    if not submission:
        raise ValueError(f"Submission not found: {submission_id}")

    # Replace existing rows for this submission
    db.query(ExtractedAnswer).filter(
        ExtractedAnswer.submission_id == sub_uuid
    ).delete()

    for question_id, answer_text in answers.items():
        db.add(
            ExtractedAnswer(
                submission_id=sub_uuid,
                question_id=question_id,
                answer_text=answer_text,
                page_number=1,
            )
        )
    db.commit()


def save_evaluation(
    db: Session, submission_id: str, question_id: str, result: dict[str, Any]
) -> None:
    """Persist AI grading result for one question. AI Pipeline Engineer calls per question."""
    sub_uuid = uuid.UUID(submission_id)
    existing = (
        db.query(Evaluation)
        .filter(
            Evaluation.submission_id == sub_uuid,
            Evaluation.question_id == question_id,
        )
        .first()
    )

    ai_marks = int(result["ai_marks"])
    justification = list(result.get("justification", []))
    missing_points = list(result.get("missing_points", []))

    if existing:
        existing.ai_marks = ai_marks
        existing.final_marks = ai_marks
        existing.justification = justification
        existing.missing_points = missing_points
        existing.status = EvaluationStatus.pending
    else:
        db.add(
            Evaluation(
                submission_id=sub_uuid,
                question_id=question_id,
                ai_marks=ai_marks,
                final_marks=ai_marks,
                justification=justification,
                missing_points=missing_points,
                status=EvaluationStatus.pending,
            )
        )
    db.commit()


def get_results(db: Session, submission_id: str) -> list[dict[str, Any]]:
    """Return evaluations joined with rubric and extracted answer data."""
    sub_uuid = uuid.UUID(submission_id)
    submission = db.get(Submission, sub_uuid)
    if not submission:
        raise ValueError(f"Submission not found: {submission_id}")

    evaluations = (
        db.query(Evaluation)
        .filter(Evaluation.submission_id == sub_uuid)
        .all()
    )
    rubrics = {
        r.question_id: r
        for r in db.query(Rubric).filter(Rubric.exam_id == submission.exam_id).all()
    }
    answers = {
        a.question_id: a
        for a in db.query(ExtractedAnswer)
        .filter(ExtractedAnswer.submission_id == sub_uuid)
        .all()
    }

    rows: list[dict[str, Any]] = []
    for ev in evaluations:
        rubric = rubrics.get(ev.question_id)
        answer = answers.get(ev.question_id)
        rows.append(
            {
                "question_id": ev.question_id,
                "question_text": rubric.question_text if rubric else "",
                "max_marks": rubric.max_marks if rubric else 0,
                "ai_marks": ev.ai_marks,
                "final_marks": ev.final_marks,
                "justification": ev.justification or [],
                "missing_points": ev.missing_points or [],
                "status": ev.status.value,
                "answer_text": answer.answer_text if answer else "",
                "page_number": answer.page_number if answer else 1,
            }
        )
    return rows
