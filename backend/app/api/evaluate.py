from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.evaluation import Evaluation, EvaluationStatus
from app.models.submission import Submission
from app.models.user import User, UserRole
from app.core.security import get_current_user
from app.schemas.evaluate import (
    EvaluateResponse,
    OverrideRequest,
    OverrideResponse,
    ResultItem,
)
from app.services import storage_service
from app.services.pipeline_runner import run_pipeline_background

router = APIRouter(tags=["evaluate"])


@router.post("/evaluate/{submission_id}")
def trigger_evaluation(
    submission_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in [UserRole.professor, UserRole.ta]:
        return JSONResponse(status_code=403, content={"error": "Unauthorized"})
    try:
        submission = db.get(Submission, submission_id)
        if not submission:
            return JSONResponse(
                status_code=404, content={"error": "Submission not found"}
            )

        background_tasks.add_task(run_pipeline_background, submission_id)
        return EvaluateResponse(status="processing")
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


@router.get("/results/{submission_id}")
def get_submission_results(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in [UserRole.professor, UserRole.ta]:
        return JSONResponse(status_code=403, content={"error": "Unauthorized"})
    try:
        submission = db.get(Submission, submission_id)
        if not submission:
            return JSONResponse(
                status_code=404, content={"error": "Submission not found"}
            )

        rows = storage_service.get_results(db, str(submission_id))
        return [ResultItem(**row) for row in rows]
    except ValueError as exc:
        return JSONResponse(status_code=404, content={"error": str(exc)})
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


@router.put("/override")
def override_evaluation(
    body: OverrideRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in [UserRole.professor, UserRole.ta]:
        return JSONResponse(status_code=403, content={"error": "Unauthorized"})
    try:
        evaluation = (
            db.query(Evaluation)
            .filter(
                Evaluation.submission_id == body.submission_id,
                Evaluation.question_id == body.question_id,
            )
            .first()
        )
        if not evaluation:
            return JSONResponse(
                status_code=404, content={"error": "Evaluation not found"}
            )

        evaluation.final_marks = body.final_marks
        if body.edited_justification is not None:
            evaluation.justification = body.edited_justification

        if evaluation.ai_marks == body.final_marks and body.edited_justification is None:
            evaluation.status = EvaluationStatus.approved
        else:
            evaluation.status = EvaluationStatus.overridden

        if body.override_by:
            evaluation.override_by = body.override_by
        evaluation.override_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(evaluation)

        return OverrideResponse(
            submission_id=body.submission_id,
            question_id=body.question_id,
            final_marks=evaluation.final_marks,
            status=evaluation.status,
            override_at=evaluation.override_at,
        )
    except Exception as exc:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": str(exc)})
