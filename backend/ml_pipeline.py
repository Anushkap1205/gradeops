import logging
import sys
import os

PERSON_A_PATH = os.path.expanduser("~/Desktop/gradeops-ai")
if PERSON_A_PATH not in sys.path:
    sys.path.append(PERSON_A_PATH)

import requests
from app.services.storage_service import save_extracted_answers, save_evaluation
from app.services.pipeline_runner import mark_submission_done

logger = logging.getLogger(__name__)


def run_grading_pipeline(db, submission_id: str) -> None:
    from app.models.submission import Submission
    import uuid

    submission = db.get(Submission, uuid.UUID(submission_id))
    if not submission:
        raise ValueError(f"Submission {submission_id} not found")

    exam_id = str(submission.exam_id)
    file_path = submission.file_path
    file_id = file_path.split("/")[1] if "/" in file_path else file_path

    outputs_dir = os.path.expanduser(f"~/Desktop/gradeops/backend/outputs/{file_id}")
    image_path = os.path.join(outputs_dir, "page_1.png")

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Page image not found: {image_path}")

    rubric_response = requests.get(f"http://localhost:8000/rubric/{exam_id}")
    rubric_list = rubric_response.json()

    rubric_data = {}
    rubric_max_marks = {}
    for rubric in rubric_list:
        qid = rubric["question_id"]
        criteria = " ".join(rubric.get("key_points", []))
        rubric_data[qid] = {"criteria": criteria, "max_score": rubric["max_marks"]}
        rubric_max_marks[qid] = rubric["max_marks"]

    from gradeops_ai.graph.workflow import build_workflow
    workflow = build_workflow()

    initial_state = {
        "image_path": image_path,
        "rubric_data": rubric_data,
        "submission_id": submission_id,
        "raw_text": None,
        "parsed_exam": None,
        "evaluation_result": None,
        "error": None,
    }

    final_state = workflow.invoke(initial_state)

    if final_state.get("error"):
        raise RuntimeError(f"Pipeline error: {final_state['error']}")

    parsed_exam = final_state.get("parsed_exam")
    if parsed_exam:
        answers = {a.question_id: a.student_answer for a in parsed_exam.answers}
        save_extracted_answers(db, submission_id, answers)

    evaluation_result = final_state.get("evaluation_result")
    if evaluation_result:
        for result in evaluation_result.results:
            max_marks = rubric_max_marks.get(result.question_id, 10)
            ai_marks = min(int(round(result.score)), max_marks)
            save_evaluation(db, submission_id, result.question_id, {
                "ai_marks": ai_marks,
                "justification": [result.feedback],
                "missing_points": ["Flagged for human review"] if result.needs_human_review else [],
            })

    mark_submission_done(db, submission_id)
    logger.info("Pipeline completed for submission %s", submission_id)
