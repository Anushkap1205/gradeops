import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class EvaluationStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    overridden = "overridden"


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id"), nullable=False)
    question_id: Mapped[str] = mapped_column(String(64), nullable=False)
    ai_marks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    final_marks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    justification: Mapped[list] = mapped_column(
        JSON, nullable=False, server_default="[]"
    )
    missing_points: Mapped[list] = mapped_column(
        JSON, nullable=False, server_default="[]"
    )
    status: Mapped[EvaluationStatus] = mapped_column(
        Enum(EvaluationStatus, name="evaluation_status"),
        nullable=False,
        default=EvaluationStatus.pending,
    )
    override_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    override_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    submission = relationship("Submission", back_populates="evaluations")
    override_user = relationship("User", back_populates="overrides")
