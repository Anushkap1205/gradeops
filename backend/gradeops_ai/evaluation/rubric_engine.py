from typing import Dict, Any

def format_rubric_for_prompt(rubric_data: Dict[str, Any], question_id: str) -> str:
    """
    Extracts and formats the rubric for a specific question into a readable string for the prompt.
    Assumes rubric_data is a dictionary mapping question IDs to rubric details.
    """
    if not rubric_data:
        return "No rubric provided. Grade based on general correctness."
        
    question_rubric = rubric_data.get(question_id)
    if not question_rubric:
        return "No specific rubric provided for this question. Grade based on general correctness."
    
    criteria = question_rubric.get("criteria", "No specific criteria")
    max_score = question_rubric.get("max_score", "Unknown")
    
    return f"Max Score: {max_score}\nGrading Criteria: {criteria}"
