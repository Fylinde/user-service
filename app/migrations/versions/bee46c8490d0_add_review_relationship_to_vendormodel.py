"""Add review relationship to VendorModel

Revision ID: bee46c8490d0
Revises: 2828836248b3
Create Date: 2024-08-05 12:58:46.419160

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'bee46c8490d0'
down_revision = '2828836248b3'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # Check if the 'vendor_id' column already exists
    if 'vendor_id' not in [col['name'] for col in inspector.get_columns('products')]:
        with op.batch_alter_table('products') as batch_op:
            batch_op.add_column(sa.Column('vendor_id', sa.Integer(), nullable=True))
            batch_op.create_foreign_key('fk_vendor', 'vendors', ['vendor_id'], ['id'])

def downgrade():
    with op.batch_alter_table('products') as batch_op:
        batch_op.drop_constraint('fk_vendor', type_='foreignkey')
        batch_op.drop_column('vendor_id')
