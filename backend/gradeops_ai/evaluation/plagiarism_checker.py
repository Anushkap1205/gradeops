import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class PlagiarismMatch(BaseModel):
    submission_a_id: int = Field(description="ID of the first submission")
    submission_b_id: int = Field(description="ID of the second submission")
    explanation: str = Field(description="Why these are flagged as highly similar logic structures.")

class PlagiarismReport(BaseModel):
    matches: list[PlagiarismMatch]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AI TA assistant looking for highly similar logic structures or identical phrasing across students' exam answers. You will be provided with a list of answers. Flag any that are suspiciously similar."),
    ("user", "Question: {question_text}\n\nAnswers:\n{answers}\n\nAre there any highly similar logic structures across these papers?")
])

def check_plagiarism(question_text: str, answers: dict[int, str]) -> list[PlagiarismMatch]:
    llm = ChatOpenAI(model="gpt-4o", temperature=0).with_structured_output(PlagiarismReport)
    answers_text = ""
    for sub_id, ans in answers.items():
        answers_text += f"Submission ID {sub_id}:\n{ans}\n\n"
    
    chain = prompt | llm
    result = chain.invoke({"question_text": question_text, "answers": answers_text})
    return result.matches if result else []
