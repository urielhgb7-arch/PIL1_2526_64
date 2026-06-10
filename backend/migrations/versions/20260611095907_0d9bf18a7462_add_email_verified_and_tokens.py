"""add email_verified column and email_tokens table

Revision ID: 20260611095907
Revises: ee58746572c1
Create Date: 2026-06-11 09:59:07.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '20260611095907'
down_revision = 'ee58746572c1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='0'))
    op.create_table('email_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=128), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )


def downgrade():
    op.drop_table('email_tokens')
    op.drop_column('users', 'email_verified')
