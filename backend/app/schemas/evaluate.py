import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.evaluation import EvaluationStatus


class EvaluateResponse(BaseModel):
    status: str


class ResultItem(BaseModel):
    question_id: str
    question_text: str
    ai_marks: int
    max_marks: int
    final_marks: int
    justification: list[str]
    missing_points: list[str]
    status: EvaluationStatus
    answer_text: str | None = None
    page_number: int | None = None


class OverrideRequest(BaseModel):
    submission_id: uuid.UUID
    question_id: str
    final_marks: int = Field(ge=0)
    edited_justification: list[str] | None = None
    override_by: uuid.UUID | None = None


class OverrideResponse(BaseModel):
    submission_id: uuid.UUID
    question_id: str
    final_marks: int
    status: EvaluationStatus
    override_at: datetime | None
