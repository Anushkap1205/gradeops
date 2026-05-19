from gradeops_ai.graph.state import GraphState
from gradeops_ai.ocr.ocr_pipeline import run_ocr
from gradeops_ai.parser.question_parser import parse_exam_text
from gradeops_ai.evaluation.evaluator import evaluate_exam

def extract_text_node(state: GraphState) -> GraphState:
    image_path = state["image_path"]
    
    result = run_ocr(image_path)
    
    if result.get("error"):
        return {"error": result["message"], "submission_id": result.get("submission_id")}
        
    return {
        "raw_text": result["raw_text"],
        "submission_id": result["submission_id"],
        "error": None
    }

def parse_text_node(state: GraphState) -> GraphState:
    raw_text = state.get("raw_text")
    if not raw_text:
        return {"error": "No raw text available for parsing"}
        
    try:
        parsed_exam = parse_exam_text(raw_text)
        return {"parsed_exam": parsed_exam, "error": None}
    except Exception as e:
        return {"error": f"Failed to parse text: {str(e)}"}

def evaluate_node(state: GraphState) -> GraphState:
    parsed_exam = state.get("parsed_exam")
    rubric_data = state.get("rubric_data", {})
    submission_id = state.get("submission_id", "unknown")
    
    if not parsed_exam:
        return {"error": "No parsed exam available for evaluation"}
        
    try:
        evaluation_result = evaluate_exam(parsed_exam, rubric_data, submission_id)
        return {"evaluation_result": evaluation_result, "error": None}
    except Exception as e:
        return {"error": f"Failed to evaluate exam: {str(e)}"}
