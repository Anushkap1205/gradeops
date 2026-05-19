from langchain_core.prompts import ChatPromptTemplate

grading_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert, impartial exam grader. Your task is to evaluate a student's answer "
        "against a specific grading rubric. Be strict but fair. Provide a numerical score and "
        "detailed feedback explaining your reasoning based on the criteria. If the answer is "
        "highly ambiguous or you are unsure, flag it for human review."
    ),
    (
        "user",
        "Question ID: {question_id}\n\nRubric:\n{rubric_text}\n\nStudent Answer:\n{student_answer}"
    )
])
