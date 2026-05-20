"""add plagiarism

Revision ID: 003_add_plagiarism
Revises: 002_add_password
Create Date: 2026-05-20 12:05:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '003_add_plagiarism'
down_revision: Union[str, None] = '002_add_password'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('plagiarism_flags',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('exam_id', sa.Integer(), nullable=False),
    sa.Column('question_id', sa.String(length=64), nullable=False),
    sa.Column('submission_a_id', sa.Integer(), nullable=False),
    sa.Column('submission_b_id', sa.Integer(), nullable=False),
    sa.Column('explanation', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['exam_id'], ['exams.id'], ),
    sa.ForeignKeyConstraint(['submission_a_id'], ['submissions.id'], ),
    sa.ForeignKeyConstraint(['submission_b_id'], ['submissions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('plagiarism_flags')
