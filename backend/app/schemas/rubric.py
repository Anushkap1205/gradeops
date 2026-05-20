from pydantic import BaseModel, Field


class RubricItemCreate(BaseModel):
    question_id: str
    question_text: str
    max_marks: int = Field(ge=0)
    key_points: list[str] = Field(default_factory=list)


class RubricCreateRequest(BaseModel):
    exam_id: int
    rubrics: list[RubricItemCreate]


class RubricResponse(BaseModel):
    id: int
    exam_id: int
    question_id: str
    question_text: str
    max_marks: int
    key_points: list[str]

    model_config = {"from_attributes": True}


class RubricCreateResponse(BaseModel):
    rubric_ids: list[int]
