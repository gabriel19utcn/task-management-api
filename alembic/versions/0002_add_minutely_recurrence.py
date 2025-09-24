"""add minutely recurrence interval

Revision ID: 0002_minutely
Revises: 0001_init
Create Date: 2025-09-21 17:34:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "0002_minutely"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add the new 'minutely' value to the recurrenceinterval enum (only if not exists)
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'minutely' AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'recurrenceinterval')) THEN
                ALTER TYPE recurrenceinterval ADD VALUE 'minutely';
            END IF;
        END $$;
    """
    )


def downgrade() -> None:
    # PostgreSQL doesn't support removing enum values easily
    # This would require recreating the enum and updating all references
    pass
