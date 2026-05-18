"""
Person A: implement run_grading_pipeline(db, submission_id).

Use:
  - app.services.storage_service.save_extracted_answers
  - app.services.storage_service.save_evaluation
  - app.services.pipeline_runner.mark_submission_done
  - GET rubrics via Rubric model / internal API
  - Page images under outputs/{file_id}/page_N.png (file_id from submission.file_path)
"""

from sqlalchemy.orm import Session

from app.services.pipeline_runner import mark_submission_done


def run_grading_pipeline(db: Session, submission_id: str) -> None:
    """
    Entry point invoked by POST /evaluate background task.
    Replace this body with LangGraph + OCR + evaluation logic.
    """
    mark_submission_done(db, submission_id)
