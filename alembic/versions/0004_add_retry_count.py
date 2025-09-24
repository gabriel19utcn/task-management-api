"""add retry_count to tasks table

Revision ID: 0004_retry_count
Revises: 0003_integer_ids
Create Date: 2025-09-22 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0004_retry_count'
down_revision = '0003_integer_ids'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add retry_count column to tasks table."""
    # Add retry_count column with default value of 0
    op.add_column('tasks', sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    """Remove retry_count column from tasks table."""
    # Drop retry_count column
    op.drop_column('tasks', 'retry_count')