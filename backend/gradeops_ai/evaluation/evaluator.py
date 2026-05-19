import os
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from gradeops_ai.evaluation.prompts import grading_prompt
from gradeops_ai.evaluation.output_parser import SingleEvaluationResult, ExamEvaluationResult
from gradeops_ai.evaluation.rubric_engine import format_rubric_for_prompt
from gradeops_ai.parser.schema import ParsedExam

def evaluate_exam(parsed_exam: ParsedExam, rubric_data: Dict[str, Any], submission_id: str) -> ExamEvaluationResult:
    llm = ChatGroq(model="llama3-70b-8192", temperature=0)
    structured_llm = llm.with_structured_output(SingleEvaluationResult)
    
    chain = grading_prompt | structured_llm
    
    results: List[SingleEvaluationResult] = []
    
    for answer in parsed_exam.answers:
        rubric_text = format_rubric_for_prompt(rubric_data, answer.question_id)
        
        result = chain.invoke({
            "question_id": answer.question_id,
            "rubric_text": rubric_text,
            "student_answer": answer.student_answer
        })
        
        result.question_id = answer.question_id
        results.append(result)
        
    return ExamEvaluationResult(submission_id=submission_id, results=results)
