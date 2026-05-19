from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from .schema import ParsedExam

def parse_exam_text(raw_text: str) -> ParsedExam:
    """
    Parses raw OCR text into structured Question/Answer pairs using an LLM.
    """
    llm = ChatGroq(model="llama3-70b-8192", temperature=0)
    
    structured_llm = llm.with_structured_output(ParsedExam)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert exam digitizer. Your task is to take raw, potentially messy OCR text from an exam and extract each question ID/number and the corresponding student's answer. Ensure you capture the full answer text provided by the student. Ignore any general instructions or unrelated text. Do not evaluate the answer."),
        ("user", "Here is the raw OCR text:\n\n{raw_text}")
    ])
    
    chain = prompt | structured_llm
    
    result = chain.invoke({"raw_text": raw_text})
    return result
