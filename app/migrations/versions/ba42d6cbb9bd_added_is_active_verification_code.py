"""Added is_active,verification_code

Revision ID: ba42d6cbb9bd
Revises: 9f79e7706a61
Create Date: 2024-09-08 11:38:11.600125

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ba42d6cbb9bd'
down_revision = '9f79e7706a61'
branch_labels = None
depends_on = None


def upgrade():
    # Manually add the columns to the users table
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')))
    op.add_column('users', sa.Column('verification_code', sa.String(), nullable=True))


def downgrade():
    # Drop the columns in case of downgrade
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'verification_code')
