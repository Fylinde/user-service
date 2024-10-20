"""updating

Revision ID: 91ed33088ed3
Revises: fce67f50164f
Create Date: 2024-09-22 13:43:58.293018

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '91ed33088ed3'
down_revision = 'fce67f50164f'
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

    # Repeat similar blocks for 'customer_events', 'customer_notes', 'group_permissions', 'staff_notification_recipients', and 'user_groups' tables

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

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name = 'language_code'
        ) THEN
            ALTER TABLE users ADD COLUMN language_code VARCHAR(35);
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
            AND column_name = 'is_admin'
        ) THEN
            ALTER TABLE users ADD COLUMN is_admin BOOLEAN;
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
            AND column_name = 'verification_code'
        ) THEN
            ALTER TABLE users ADD COLUMN verification_code VARCHAR;
        END IF;
    END $$;
    """)

    # Ensure all the other column alterations and drops are conditional in a similar way.

def downgrade():
    # Drop tables and columns in a similar conditional manner
    # Ensure these checks use `IF EXISTS` to avoid errors on non-existing elements
    pass
