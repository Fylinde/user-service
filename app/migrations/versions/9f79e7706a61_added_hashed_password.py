"""Added hashed_password

Revision ID: 9f79e7706a61
Revises: 908d8c67976a
Create Date: 2024-09-08 10:52:17.260721

"""
from alembic import op



# revision identifiers, used by Alembic.
revision = '9f79e7706a61'
down_revision = '908d8c67976a'
branch_labels = None
depends_on = None


def upgrade():
    # Add the hashed_password column if it doesn't already exist
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name = 'hashed_password'
        ) THEN
            ALTER TABLE users ADD COLUMN hashed_password VARCHAR(255) NOT NULL;
        END IF;
    END $$;
    """)


def downgrade():
    # Drop the hashed_password column if it exists
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name = 'hashed_password'
        ) THEN
            ALTER TABLE users DROP COLUMN hashed_password;
        END IF;
    END $$;
    """)
