from pydantic import BaseModel, Field
from typing import List

class ParsedAnswer(BaseModel):
    question_id: str = Field(description="The identifier for the question, e.g., '1a', '2', 'Q3'")
    student_answer: str = Field(description="The text of the student's answer for this question")

class ParsedExam(BaseModel):
    answers: List[ParsedAnswer] = Field(description="A list of all parsed answers from the exam")
