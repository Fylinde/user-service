"""Added is_active,verification_code

Revision ID: ba42d6cbb9bd
Revises: 9f79e7706a61
Create Date: 2024-09-08 11:38:11.600125

"""
from alembic import op



# revision identifiers, used by Alembic.
revision = 'ba42d6cbb9bd'
down_revision = '9f79e7706a61'
branch_labels = None
depends_on = None


def upgrade():
    # Add the is_active column if it doesn't already exist
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name = 'is_active'
        ) THEN
            ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE;
        END IF;
    END $$;
    """)

    # Add the verification_code column if it doesn't already exist
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


def downgrade():
    # Drop the is_active column if it exists
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name = 'is_active'
        ) THEN
            ALTER TABLE users DROP COLUMN is_active;
        END IF;
    END $$;
    """)

    # Drop the verification_code column if it exists
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name = 'verification_code'
        ) THEN
            ALTER TABLE users DROP COLUMN verification_code;
        END IF;
    END $$;
    """)
