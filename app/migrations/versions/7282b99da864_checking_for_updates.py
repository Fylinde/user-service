from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '7282b99da864'
down_revision = '19b7e0d5b01b'
branch_labels = None
depends_on = None

def upgrade():
    # Drop foreign key constraints if they exist
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 
            FROM information_schema.table_constraints 
            WHERE constraint_name = 'reviews_product_id_fkey' 
            AND table_name = 'reviews'
        ) THEN
            ALTER TABLE reviews DROP CONSTRAINT reviews_product_id_fkey;
        END IF;
    END $$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 
            FROM information_schema.table_constraints 
            WHERE constraint_name = 'orders_product_id_fkey' 
            AND table_name = 'orders'
        ) THEN
            ALTER TABLE orders DROP CONSTRAINT orders_product_id_fkey;
        END IF;
    END $$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 
            FROM information_schema.table_constraints 
            WHERE constraint_name = 'wishlists_product_id_fkey' 
            AND table_name = 'wishlists'
        ) THEN
            ALTER TABLE wishlists DROP CONSTRAINT wishlists_product_id_fkey;
        END IF;
    END $$;
    """)

    # Drop 'products' table and its indexes if they exist
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 
            FROM information_schema.tables 
            WHERE table_name = 'products'
        ) THEN
            DROP INDEX IF EXISTS ix_products_id;
            DROP INDEX IF EXISTS ix_products_name;
            DROP TABLE products;
        END IF;
    END $$;
    """)

    # Drop 'orders' table and its index if they exist
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 
            FROM information_schema.tables 
            WHERE table_name = 'orders'
        ) THEN
            DROP INDEX IF EXISTS ix_orders_id;
            DROP TABLE orders;
        END IF;
    END $$;
    """)

    # Drop 'addresses' table and its index if they exist
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 
            FROM information_schema.tables 
            WHERE table_name = 'addresses'
        ) THEN
            DROP INDEX IF EXISTS ix_addresses_id;
            DROP TABLE addresses;
        END IF;
    END $$;
    """)

    # Add new columns to 'users' if they don't exist
    columns_to_add = [
        ('notification_preferences', sa.String()),
        ('date_of_birth', sa.String()),
        ('gender', sa.String(length=10)),
        ('is_email_verified', sa.Boolean()),
        ('is_phone_verified', sa.Boolean()),
        ('two_factor_enabled', sa.Boolean()),
        ('two_factor_secret', sa.String()),
        ('created_at', sa.TIMESTAMP()),
        ('updated_at', sa.TIMESTAMP()),
        ('subscription_status', sa.String())
    ]

    for column_name, column_type in columns_to_add:
        op.execute(f"""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name = '{column_name}'
            ) THEN
                ALTER TABLE users ADD COLUMN {column_name} {column_type};
            END IF;
        END $$;
        """)

    # Alter column type for 'preferences' if it exists
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name = 'preferences'
        ) THEN
            ALTER TABLE users 
            ALTER COLUMN preferences 
            TYPE JSON 
            USING preferences::json;
        END IF;
    END $$;
    """)

def downgrade():
    # Recreate constraints during downgrade only if the table and column exist
    # Similar logic for recreating dropped tables like 'products', 'orders', 'addresses', etc.
    # Example for 'products' table:

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 
            FROM information_schema.tables 
            WHERE table_name = 'products'
        ) THEN
            CREATE TABLE products (
                id SERIAL PRIMARY KEY,
                name VARCHAR,
                description VARCHAR,
                vendor_id INTEGER REFERENCES vendors(id),
                price DOUBLE PRECISION NOT NULL
            );
            CREATE INDEX ix_products_name ON products (name);
            CREATE INDEX ix_products_id ON products (id);
        END IF;
    END $$;
    """)

    # Recreate the rest of the downgrade logic conditionally
    # Ensure that each element is recreated only if it does not already exist
