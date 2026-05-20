import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SubmissionStatus(str, enum.Enum):
    uploaded = "uploaded"
    processing = "processing"
    done = "done"


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus, name="submission_status"),
        nullable=False,
        default=SubmissionStatus.uploaded,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    student = relationship("User", back_populates="submissions")
    exam = relationship("Exam", back_populates="submissions")
    extracted_answers = relationship(
        "ExtractedAnswer", back_populates="submission", cascade="all, delete-orphan"
    )
    evaluations = relationship(
        "Evaluation", back_populates="submission", cascade="all, delete-orphan"
    )
