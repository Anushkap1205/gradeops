from pydantic import BaseModel, Field

class SingleEvaluationResult(BaseModel):
    question_id: str = Field(description="The identifier of the question evaluated")
    score: float = Field(description="The numeric score awarded to the answer")
    feedback: str = Field(description="Detailed feedback explaining the score based on the rubric")
    needs_human_review: bool = Field(description="True if the model is unsure or if the answer is borderline")

class ExamEvaluationResult(BaseModel):
    submission_id: str = Field(description="The identifier of the submission")
    results: list[SingleEvaluationResult] = Field(description="A list of evaluation results for all questions")
