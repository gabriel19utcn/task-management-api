"""switch to integer IDs for better performance and indexing

Revision ID: 0003_integer_ids
Revises: 0002_minutely
Create Date: 2025-09-21 18:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0003_integer_ids'
down_revision = '0002_minutely'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop existing tables and recreate with integer IDs
    # This is a breaking change, but provides better performance

    # Drop foreign key constraint first
    try:
        op.drop_constraint('tasks_recurrence_rule_id_fkey', 'tasks', type_='foreignkey')
    except Exception:
        pass  # Constraint might not exist

    # Drop indexes
    try:
        op.drop_index('ix_tasks_priority', table_name='tasks')
        op.drop_index('ix_tasks_scheduled_for', table_name='tasks')
        op.drop_index('ix_tasks_recurrence_rule_id', table_name='tasks')
    except Exception:
        pass  # Indexes might not exist

    # Drop tables
    op.drop_table('tasks')
    op.drop_table('recurrence_rules')

    # Recreate recurrence_rules table with integer ID
    op.create_table(
        'recurrence_rules',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('interval_type', sa.Enum('minutely', 'hourly', 'daily', name='recurrenceinterval', create_type=False), nullable=False),
        sa.Column('interval_value', sa.Integer(), nullable=False),
        sa.Column('next_run_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('base_payload', sa.JSON(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='5'),
    )

    # Recreate tasks table with integer ID
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('type', sa.Enum('single', 'batch', name='tasktype', create_type=False), nullable=False),
        sa.Column('status', sa.Enum('pending', 'queued', 'running', 'success', 'failed', 'revoked', name='taskstatus', create_type=False), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('a', sa.Integer(), nullable=True),
        sa.Column('b', sa.Integer(), nullable=True),
        sa.Column('result', sa.Integer(), nullable=True),
        sa.Column('pairs', sa.JSON(), nullable=True),
        sa.Column('results', sa.JSON(), nullable=True),
        sa.Column('scheduled_for', sa.DateTime(timezone=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('recurrence_rule_id', sa.Integer(), sa.ForeignKey('recurrence_rules.id'), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Recreate indexes
    op.create_index('ix_tasks_priority', 'tasks', ['priority'])
    op.create_index('ix_tasks_scheduled_for', 'tasks', ['scheduled_for'])
    op.create_index('ix_tasks_recurrence_rule_id', 'tasks', ['recurrence_rule_id'])


def downgrade() -> None:
    # Drop integer ID tables and recreate UUID tables
    op.drop_index('ix_tasks_priority', table_name='tasks')
    op.drop_index('ix_tasks_scheduled_for', table_name='tasks')
    op.drop_index('ix_tasks_recurrence_rule_id', table_name='tasks')
    op.drop_table('tasks')
    op.drop_table('recurrence_rules')

    # Recreate with UUID (original schema)
    op.create_table(
        'recurrence_rules',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('interval_type', sa.Enum('minutely', 'hourly', 'daily', name='recurrenceinterval'), nullable=False),
        sa.Column('interval_value', sa.Integer(), nullable=False),
        sa.Column('next_run_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('base_payload', sa.JSON(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='5'),
    )

    op.create_table(
        'tasks',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('type', sa.Enum('single', 'batch', name='tasktype'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'queued', 'running', 'success', 'failed', 'revoked', name='taskstatus'), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('a', sa.Integer(), nullable=True),
        sa.Column('b', sa.Integer(), nullable=True),
        sa.Column('result', sa.Integer(), nullable=True),
        sa.Column('pairs', sa.JSON(), nullable=True),
        sa.Column('results', sa.JSON(), nullable=True),
        sa.Column('scheduled_for', sa.DateTime(timezone=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('recurrence_rule_id', sa.UUID(), sa.ForeignKey('recurrence_rules.id'), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_tasks_priority', 'tasks', ['priority'])
    op.create_index('ix_tasks_scheduled_for', 'tasks', ['scheduled_for'])
    op.create_index('ix_tasks_recurrence_rule_id', 'tasks', ['recurrence_rule_id'])