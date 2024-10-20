"""Added full name and phone number

Revision ID: fce67f50164f
Revises: 7u8654hy98765
Create Date: 2024-09-22 13:39:19.116152

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'fce67f50164f'
down_revision = '7u8654hy98765'
branch_labels = None
depends_on = None


def upgrade():
    # Create 'groups' table if it doesn't exist
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 
            FROM information_schema.tables 
            WHERE table_name = 'groups'
        ) THEN
            CREATE TABLE groups (
                id SERIAL PRIMARY KEY,
                name VARCHAR(150) NOT NULL UNIQUE
            );
            CREATE INDEX ix_groups_id ON groups (id);
        END IF;
    END $$;
    """)

    # Create 'permissions' table if it doesn't exist
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 
            FROM information_schema.tables 
            WHERE table_name = 'permissions'
        ) THEN
            CREATE TABLE permissions (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE
            );
            CREATE INDEX ix_permissions_id ON permissions (id);
        END IF;
    END $$;
    """)

    # Create 'addresses' table if it doesn't exist
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 
            FROM information_schema.tables 
            WHERE table_name = 'addresses'
        ) THEN
            CREATE TABLE addresses (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(256),
                last_name VARCHAR(256),
                company_name VARCHAR(256),
                street_address_1 VARCHAR(256),
                street_address_2 VARCHAR(256),
                city VARCHAR(256),
                city_area VARCHAR(128),
                postal_code VARCHAR(20),
                country VARCHAR(2) NOT NULL,
                country_area VARCHAR(128),
                phone VARCHAR(20),
                validation_skipped BOOLEAN,
                user_id INTEGER REFERENCES users(id)
            );
            CREATE INDEX ix_addresses_id ON addresses (id);
        END IF;
    END $$;
    """)

    # Add columns to 'users' table if they don't exist
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name = 'first_name'
        ) THEN
            ALTER TABLE users ADD COLUMN first_name VARCHAR(128);
        END IF;
    END $$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name = 'last_name'
        ) THEN
            ALTER TABLE users ADD COLUMN last_name VARCHAR(128);
        END IF;
    END $$;
    """)

    # Repeat for other columns...

    # Additional tables and columns can be handled in a similar manner

def downgrade():
    # Drop the tables if they exist, with foreign key constraints handled appropriately
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 
            FROM information_schema.tables 
            WHERE table_name = 'user_groups'
        ) THEN
            DROP TABLE user_groups;
        END IF;
    END $$;
    """)

    # Repeat for all other tables and columns as needed

