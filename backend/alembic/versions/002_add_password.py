"""add hashed_password

Revision ID: 002_add_password
Revises: 001_initial
Create Date: 2026-05-20 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_add_password'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'hashed_password')
