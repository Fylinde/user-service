"""Added is_admin

Revision ID: 7u8654hy98765
Revises: ba42d6cbb9bd
Create Date: 2024-09-08 11:38:11.600125

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7u8654hy98765'
down_revision = 'ba42d6cbb9bd'
branch_labels = None
depends_on = None


def upgrade():
    # Manually add the columns to the users table
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default=sa.text('true')))
   


def downgrade():
    # Drop the columns in case of downgrade
    op.drop_column('users', 'is_admin')
    
