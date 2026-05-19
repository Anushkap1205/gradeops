import importlib
import logging
import uuid

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.submission import Submission, SubmissionStatus

logger = logging.getLogger(__name__)


def run_pipeline_background(submission_id: str) -> None:
    """Background task entry: load DB session and invoke AI Pipeline Engineer's pipeline module."""
    db = SessionLocal()
    try:
        submission = db.get(Submission, uuid.UUID(submission_id))
        if not submission:
            logger.error("Submission %s not found for pipeline", submission_id)
            return

        submission.status = SubmissionStatus.processing
        db.commit()

        module = importlib.import_module(settings.pipeline_module)
        run_fn = getattr(module, "run_grading_pipeline", None)
        if run_fn is None:
            raise RuntimeError(
                f"Module {settings.pipeline_module} must define run_grading_pipeline(db, submission_id)"
            )

        run_fn(db, submission_id)

        submission = db.get(Submission, uuid.UUID(submission_id))
        if submission and submission.status == SubmissionStatus.processing:
            submission.status = SubmissionStatus.done
            db.commit()
    except Exception:
        logger.exception("Grading pipeline failed for submission %s", submission_id)
        db.rollback()
        submission = db.get(Submission, uuid.UUID(submission_id))
        if submission:
            submission.status = SubmissionStatus.uploaded
            db.commit()
    finally:
        db.close()


def mark_submission_done(db: Session, submission_id: str) -> None:
    """Helper for AI Pipeline Engineer to call when the graph finishes successfully."""
    submission = db.get(Submission, uuid.UUID(submission_id))
    if submission:
        submission.status = SubmissionStatus.done
        db.commit()
