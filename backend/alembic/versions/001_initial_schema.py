"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-05-18

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_role = postgresql.ENUM(
        "professor", "ta", "student", name="user_role", create_type=True
    )
    submission_status = postgresql.ENUM(
        "uploaded", "processing", "done", name="submission_status", create_type=True
    )
    evaluation_status = postgresql.ENUM(
        "pending", "approved", "overridden", name="evaluation_status", create_type=True
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

    op.create_table(
        "exams",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("course", sa.String(255), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
    )

    op.create_table(
        "submissions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("exam_id", sa.Integer(), nullable=False),
        sa.Column("file_path", sa.String(512), nullable=False),
        sa.Column("status", submission_status, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["exam_id"], ["exams.id"]),
    )

    op.create_table(
        "rubrics",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("exam_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.String(64), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("max_marks", sa.Integer(), nullable=False),
        sa.Column("key_points", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["exam_id"], ["exams.id"]),
    )

    op.create_table(
        "extracted_answers",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("submission_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.String(64), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["submission_id"], ["submissions.id"]),
    )

    op.create_table(
        "evaluations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("submission_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.String(64), nullable=False),
        sa.Column("ai_marks", sa.Integer(), nullable=False),
        sa.Column("final_marks", sa.Integer(), nullable=False),
        sa.Column("justification", sa.JSON(), nullable=False),
        sa.Column("missing_points", sa.JSON(), nullable=False),
        sa.Column("status", evaluation_status, nullable=False),
        sa.Column("override_by", sa.Integer(), nullable=True),
        sa.Column("override_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["submission_id"], ["submissions.id"]),
        sa.ForeignKeyConstraint(["override_by"], ["users.id"]),
    )


def downgrade() -> None:
    op.drop_table("evaluations")
    op.drop_table("extracted_answers")
    op.drop_table("rubrics")
    op.drop_table("submissions")
    op.drop_table("exams")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS evaluation_status")
    op.execute("DROP TYPE IF EXISTS submission_status")
    op.execute("DROP TYPE IF EXISTS user_role")
