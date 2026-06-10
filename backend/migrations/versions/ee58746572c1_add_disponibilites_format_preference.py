"""add disponibilites format_preference

Revision ID: ee58746572c1
Revises: bb61556b3a65
Create Date: 2026-06-10 11:58:55.590379

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'ee58746572c1'
down_revision = 'bb61556b3a65'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('demands', sa.Column('format_preference', sa.String(length=20), nullable=True))
    op.execute("ALTER TABLE demands ALTER COLUMN urgence TYPE VARCHAR(20) USING urgence::varchar")
    op.execute("ALTER TABLE demands ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE offers ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE matching ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC'")


def downgrade():
    op.execute("ALTER TABLE matching ALTER COLUMN created_at TYPE TIMESTAMP")
    op.execute("ALTER TABLE offers ALTER COLUMN created_at TYPE TIMESTAMP")
    op.execute("ALTER TABLE demands ALTER COLUMN created_at TYPE TIMESTAMP")
    op.execute("ALTER TABLE demands ALTER COLUMN urgence TYPE INTEGER USING urgence::integer")
    op.drop_column('demands', 'format_preference')
