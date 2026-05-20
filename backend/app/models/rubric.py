from sqlalchemy import ForeignKey, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Rubric(Base):
    __tablename__ = "rubrics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"), nullable=False)
    question_id: Mapped[str] = mapped_column(String(64), nullable=False)
    question_text: Mapped[str] = mapped_column(String, nullable=False)
    max_marks: Mapped[int] = mapped_column(Integer, nullable=False)
    key_points: Mapped[list] = mapped_column(
        JSON, nullable=False, server_default="[]"
    )

    exam = relationship("Exam", back_populates="rubrics")
