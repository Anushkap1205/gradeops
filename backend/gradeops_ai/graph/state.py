from typing import Dict, Any, Optional
from typing_extensions import TypedDict
from gradeops_ai.parser.schema import ParsedExam
from gradeops_ai.evaluation.output_parser import ExamEvaluationResult

class GraphState(TypedDict):
    # Inputs
    image_path: str
    rubric_data: Dict[str, Any]
    
    # Internal state
    submission_id: Optional[str]
    raw_text: Optional[str]
    parsed_exam: Optional[ParsedExam]
    
    # Outputs
    evaluation_result: Optional[ExamEvaluationResult]
    error: Optional[str]
