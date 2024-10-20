"""password_last_update

Revision ID: d4c7f7c47384
Revises: 7634fdbd629c
Create Date: 2024-10-06 15:00:38.058627

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'd4c7f7c47384'
down_revision = '7634fdbd629c'
branch_labels = None
depends_on = None

def upgrade():
    # Add the column 'password_last_updated' only if it doesn't exist
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'users'
            AND column_name = 'password_last_updated'
        ) THEN
            ALTER TABLE users ADD COLUMN password_last_updated TIMESTAMP;
        END IF;
    END $$;
    """)

def downgrade():
    # Drop the column 'password_last_updated' only if it exists
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'users'
            AND column_name = 'password_last_updated'
        ) THEN
            ALTER TABLE users DROP COLUMN password_last_updated;
        END IF;
    END $$;
    """)
