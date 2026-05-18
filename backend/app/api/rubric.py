import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.exam import Exam
from app.models.rubric import Rubric
from app.schemas.rubric import (
    RubricCreateRequest,
    RubricCreateResponse,
    RubricResponse,
)

router = APIRouter(tags=["rubric"])


@router.post("/rubric")
def create_rubrics(
    body: RubricCreateRequest,
    db: Session = Depends(get_db),
):
    try:
        if not db.get(Exam, body.exam_id):
            return JSONResponse(status_code=400, content={"error": "Exam not found"})

        created_ids: list[uuid.UUID] = []
        for item in body.rubrics:
            rubric = Rubric(
                exam_id=body.exam_id,
                question_id=item.question_id,
                question_text=item.question_text,
                max_marks=item.max_marks,
                key_points=item.key_points,
            )
            db.add(rubric)
            db.flush()
            created_ids.append(rubric.id)

        db.commit()
        return RubricCreateResponse(rubric_ids=created_ids)
    except Exception as exc:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": str(exc)})


@router.get("/rubric/{exam_id}")
def get_rubrics(exam_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        if not db.get(Exam, exam_id):
            return JSONResponse(status_code=404, content={"error": "Exam not found"})

        rubrics = db.query(Rubric).filter(Rubric.exam_id == exam_id).all()
        return [RubricResponse.model_validate(r) for r in rubrics]
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})
