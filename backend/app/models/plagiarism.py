from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class PlagiarismFlag(Base):
    __tablename__ = "plagiarism_flags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"), nullable=False)
    question_id: Mapped[str] = mapped_column(String(64), nullable=False)
    submission_a_id: Mapped[int] = mapped_column(ForeignKey("submissions.id"), nullable=False)
    submission_b_id: Mapped[int] = mapped_column(ForeignKey("submissions.id"), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    exam = relationship("Exam")
