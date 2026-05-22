"""
Review API — High-throughput TA review endpoints.

GET  /review/queue          → paginated list of pending evaluations across all submissions
POST /review/bulk-approve   → approve (or override) a batch of evaluations in one request
GET  /review/stats          → summary counts by status across the whole system
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.evaluation import Evaluation, EvaluationStatus
from app.models.extracted_answer import ExtractedAnswer
from app.models.rubric import Rubric
from app.models.submission import Submission
from app.models.user import User, UserRole

router = APIRouter(prefix="/review", tags=["review"])


# ─── Schemas ────────────────────────────────────────────────────────────────

class QueueItem(BaseModel):
    submission_id: int
    file_id: str          # folder name under uploads/ for serving images
    student_id: int
    exam_id: int
    question_id: str
    question_text: str
    max_marks: int
    ai_marks: int
    final_marks: int
    justification: list[str]
    missing_points: list[str]
    status: str
    answer_text: str
    page_number: int


class BulkAction(BaseModel):
    submission_id: int
    question_id: str
    final_marks: int = Field(ge=0)
    edited_justification: Optional[list[str]] = None


class BulkApproveRequest(BaseModel):
    actions: list[BulkAction]


class BulkApproveResponse(BaseModel):
    processed: int
    failed: int
    errors: list[str]


class ReviewStats(BaseModel):
    total: int
    pending: int
    approved: int
    overridden: int


# ─── Helpers ────────────────────────────────────────────────────────────────

def _require_ta(current_user: User):
    if current_user.role not in [UserRole.professor, UserRole.ta]:
        return JSONResponse(status_code=403, content={"error": "Unauthorized"})
    return None


def _file_id_for_submission(submission: Submission) -> str:
    """
    Derive the file_id (folder name used by the upload service) from the
    stored file_path.  The path is stored as something like:
      uploads/<file_id>/page_1.pdf   or   uploads/<file_id>/<filename>
    We return the first path component after 'uploads/'.
    """
    import os
    parts = submission.file_path.replace("\\", "/").split("/")
    # find 'uploads' segment and take the next one
    try:
        idx = next(i for i, p in enumerate(parts) if p == "uploads")
        return parts[idx + 1]
    except (StopIteration, IndexError):
        # fallback: use the directory of the file
        return os.path.basename(os.path.dirname(submission.file_path))


# ─── Endpoints ──────────────────────────────────────────────────────────────

@router.get("/queue", response_model=list[QueueItem])
def get_review_queue(
    status: Optional[str] = Query(None, description="Filter: pending | approved | overridden"),
    exam_id: Optional[int] = Query(None, description="Filter by exam"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return a flat, paginated list of evaluation items ready for TA review.
    Each item carries enough information to render the side-by-side card
    without additional round-trips.
    """
    err = _require_ta(current_user)
    if err:
        return err

    try:
        q = db.query(Evaluation)

        if status:
            try:
                q = q.filter(Evaluation.status == EvaluationStatus(status))
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"error": f"Unknown status: {status}. Use pending | approved | overridden"},
                )

        if exam_id:
            # join through submission to filter by exam
            q = q.join(Submission, Evaluation.submission_id == Submission.id).filter(
                Submission.exam_id == exam_id
            )

        evaluations = q.order_by(Evaluation.submission_id, Evaluation.question_id).offset(offset).limit(limit).all()

        # bulk-load rubrics and answers keyed by (exam_id, question_id) / (sub_id, q_id)
        sub_ids = list({ev.submission_id for ev in evaluations})
        submissions = {s.id: s for s in db.query(Submission).filter(Submission.id.in_(sub_ids)).all()}

        exam_ids = list({s.exam_id for s in submissions.values()})
        rubrics: dict[tuple, Rubric] = {
            (r.exam_id, r.question_id): r
            for r in db.query(Rubric).filter(Rubric.exam_id.in_(exam_ids)).all()
        }

        answers: dict[tuple, ExtractedAnswer] = {
            (a.submission_id, a.question_id): a
            for a in db.query(ExtractedAnswer)
            .filter(ExtractedAnswer.submission_id.in_(sub_ids))
            .all()
        }

        items: list[QueueItem] = []
        for ev in evaluations:
            sub = submissions.get(ev.submission_id)
            if not sub:
                continue
            rubric = rubrics.get((sub.exam_id, ev.question_id))
            answer = answers.get((ev.submission_id, ev.question_id))
            items.append(
                QueueItem(
                    submission_id=ev.submission_id,
                    file_id=_file_id_for_submission(sub),
                    student_id=sub.student_id,
                    exam_id=sub.exam_id,
                    question_id=ev.question_id,
                    question_text=rubric.question_text if rubric else "",
                    max_marks=rubric.max_marks if rubric else 0,
                    ai_marks=ev.ai_marks,
                    final_marks=ev.final_marks,
                    justification=ev.justification or [],
                    missing_points=ev.missing_points or [],
                    status=ev.status.value,
                    answer_text=answer.answer_text if answer else "",
                    page_number=answer.page_number if answer else 1,
                )
            )

        return items

    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


@router.post("/bulk-approve", response_model=BulkApproveResponse)
def bulk_approve(
    body: BulkApproveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Process a batch of TA decisions in a single request.
    If final_marks == ai_marks (and no edited_justification) → approved.
    Otherwise → overridden.
    """
    err = _require_ta(current_user)
    if err:
        return err

    processed = 0
    failed = 0
    errors: list[str] = []

    for action in body.actions:
        try:
            evaluation = (
                db.query(Evaluation)
                .filter(
                    Evaluation.submission_id == action.submission_id,
                    Evaluation.question_id == action.question_id,
                )
                .first()
            )
            if not evaluation:
                raise ValueError(
                    f"Evaluation not found: sub={action.submission_id} q={action.question_id}"
                )

            evaluation.final_marks = action.final_marks
            if action.edited_justification is not None:
                evaluation.justification = action.edited_justification

            if evaluation.ai_marks == action.final_marks and action.edited_justification is None:
                evaluation.status = EvaluationStatus.approved
            else:
                evaluation.status = EvaluationStatus.overridden

            evaluation.override_by = current_user.id
            evaluation.override_at = datetime.now(timezone.utc)
            processed += 1

        except Exception as exc:
            failed += 1
            errors.append(str(exc))

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": f"Commit failed: {exc}"})

    return BulkApproveResponse(processed=processed, failed=failed, errors=errors)


@router.get("/stats", response_model=ReviewStats)
def get_review_stats(
    exam_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Aggregate counts for the header progress bar."""
    err = _require_ta(current_user)
    if err:
        return err

    try:
        q = db.query(Evaluation)
        if exam_id:
            q = q.join(Submission, Evaluation.submission_id == Submission.id).filter(
                Submission.exam_id == exam_id
            )

        total = q.count()
        pending = q.filter(Evaluation.status == EvaluationStatus.pending).count()
        approved = q.filter(Evaluation.status == EvaluationStatus.approved).count()
        overridden = q.filter(Evaluation.status == EvaluationStatus.overridden).count()

        return ReviewStats(total=total, pending=pending, approved=approved, overridden=overridden)

    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})
