import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "recurrence_rules",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        ),
        sa.Column(
            "interval_type",
            sa.Enum("hourly", "daily", name="recurrenceinterval"),
            nullable=False,
        ),
        sa.Column("interval_value", sa.Integer(), nullable=False),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column("base_payload", sa.JSON(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="5"),
    )

    op.create_table(
        "tasks",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        ),
        sa.Column("type", sa.Enum("single", "batch", name="tasktype"), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "queued",
                "running",
                "success",
                "failed",
                "revoked",
                name="taskstatus",
            ),
            nullable=False,
        ),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("a", sa.Integer(), nullable=True),
        sa.Column("b", sa.Integer(), nullable=True),
        sa.Column("result", sa.Integer(), nullable=True),
        sa.Column("pairs", sa.JSON(), nullable=True),
        sa.Column("results", sa.JSON(), nullable=True),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "recurrence_rule_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("recurrence_rules.id"),
            nullable=True,
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tasks_priority", "tasks", ["priority"])
    op.create_index("ix_tasks_scheduled_for", "tasks", ["scheduled_for"])
    op.create_index("ix_tasks_recurrence_rule_id", "tasks", ["recurrence_rule_id"])


def downgrade():
    op.drop_index("ix_tasks_priority", table_name="tasks")
    op.drop_index("ix_tasks_scheduled_for", table_name="tasks")
    op.drop_index("ix_tasks_recurrence_rule_id", table_name="tasks")
    op.drop_table("tasks")
    op.drop_table("recurrence_rules")
