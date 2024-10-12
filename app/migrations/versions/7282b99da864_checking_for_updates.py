from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '7282b99da864'
down_revision = '19b7e0d5b01b'
branch_labels = None
depends_on = None

def upgrade():
    # Drop foreign key constraints first
    op.drop_constraint('reviews_product_id_fkey', 'reviews', type_='foreignkey')
    op.drop_constraint('orders_product_id_fkey', 'orders', type_='foreignkey')
    op.drop_constraint('wishlists_product_id_fkey', 'wishlists', type_='foreignkey')
    
    # Now drop the table
    op.drop_index('ix_products_id', table_name='products')
    op.drop_index('ix_products_name', table_name='products')
    op.drop_table('products')

    # Other upgrade commands
    op.drop_index('ix_orders_id', table_name='orders')
    op.drop_table('orders')
    op.drop_index('ix_addresses_id', table_name='addresses')
    op.drop_table('addresses')
    
    # Adding new columns to users
    op.add_column('users', sa.Column('notification_preferences', sa.String(), nullable=True))
    op.add_column('users', sa.Column('date_of_birth', sa.String(), nullable=True))
    op.add_column('users', sa.Column('gender', sa.String(length=10), nullable=True))
    op.add_column('users', sa.Column('is_email_verified', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('is_phone_verified', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('two_factor_enabled', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('two_factor_secret', sa.String(), nullable=True))
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('subscription_status', sa.String(), nullable=True))

    # Alter column type for preferences with explicit casting
    op.alter_column('users', 'preferences',
                    type_=sa.JSON(),
                    existing_type=sa.VARCHAR(),
                    postgresql_using="preferences::json",
                    existing_nullable=True)

def downgrade():
    # Recreate constraints during downgrade
    op.create_foreign_key('reviews_product_id_fkey', 'reviews', 'products', ['product_id'], ['id'])
    op.create_foreign_key('orders_product_id_fkey', 'orders', 'products', ['product_id'], ['id'])
    op.create_foreign_key('wishlists_product_id_fkey', 'wishlists', 'products', ['product_id'], ['id'])
    
    # Recreate products table during downgrade
    op.create_table('products',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('vendor_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('price', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], name='products_vendor_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='products_pkey')
    )
    op.create_index('ix_products_name', 'products', ['name'], unique=False)
    op.create_index('ix_products_id', 'products', ['id'], unique=False)

    # Recreate other downgraded elements
    op.create_foreign_key('reviews_product_id_fkey', 'reviews', 'products', ['product_id'], ['id'])
    op.create_foreign_key('wishlists_product_id_fkey', 'wishlists', 'products', ['product_id'], ['id'])
    op.create_foreign_key('orders_product_id_fkey', 'orders', 'products', ['product_id'], ['id'])
    # Recreate rest of downgrade logic...
