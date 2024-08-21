"""Updated VendorModel

Revision ID: 19b2e038a6ad
Revises: d78e0ea53bd6
Create Date: 2024-08-14 08:55:16.649766

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '19b2e038a6ad'
down_revision = 'd78e0ea53bd6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('vendors', sa.Column('email', sa.String(length=100), nullable=True))
    op.add_column('vendors', sa.Column('rating', sa.Integer(), nullable=True))
    op.add_column('vendors', sa.Column('profile_picture', sa.String(length=255), nullable=True))
    op.add_column('vendors', sa.Column('preferences', sa.String(length=255), nullable=True))
    op.add_column('vendors', sa.Column('hashed_password', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_vendors_email'), 'vendors', ['email'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_vendors_email'), table_name='vendors')
    op.drop_column('vendors', 'hashed_password')
    op.drop_column('vendors', 'preferences')
    op.drop_column('vendors', 'profile_picture')
    op.drop_column('vendors', 'rating')
    op.drop_column('vendors', 'email')
    # ### end Alembic commands ###
