"""Added hashed_password

Revision ID: 9f79e7706a61
Revises: 908d8c67976a
Create Date: 2024-09-08 10:52:17.260721

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f79e7706a61'
down_revision = '908d8c67976a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('hashed_password', sa.String(length=255), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'hashed_password')
    # ### end Alembic commands ###
