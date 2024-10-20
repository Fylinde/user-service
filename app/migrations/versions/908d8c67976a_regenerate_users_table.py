"""Regenerate users table

Revision ID: 908d8c67976a
Revises: 8a312b84383c
Create Date: 2024-09-07 09:30:58.467321

"""
from alembic import op



# revision identifiers, used by Alembic.
revision = '908d8c67976a'
down_revision = '8a312b84383c'
branch_labels = None
depends_on = None


def upgrade():
    # Use raw SQL to create the users table only if it doesn't exist
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username VARCHAR NOT NULL,
                email VARCHAR NOT NULL,
                profile_picture VARCHAR,
                preferences VARCHAR,
                first_name VARCHAR(128),
                last_name VARCHAR(128),
                language_code VARCHAR(35),
                role VARCHAR
            );
        END IF;
    END $$;
    """)

    # Create indexes conditionally
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE tablename = 'users' AND indexname = 'ix_users_email') THEN
            CREATE UNIQUE INDEX ix_users_email ON users (email);
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE tablename = 'users' AND indexname = 'ix_users_id') THEN
            CREATE INDEX ix_users_id ON users (id);
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE tablename = 'users' AND indexname = 'ix_users_username') THEN
            CREATE UNIQUE INDEX ix_users_username ON users (username);
        END IF;
    END $$;
    """)

    # Create foreign keys conditionally
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                       WHERE table_name = 'addresses' AND constraint_type = 'FOREIGN KEY') THEN
            ALTER TABLE addresses ADD CONSTRAINT fk_addresses_user_id FOREIGN KEY (user_id) REFERENCES users (id);
        END IF;
        
        -- Repeat for each foreign key constraint as needed
        -- Replace 'addresses' and 'fk_addresses_user_id' with the correct table and constraint names
    END $$;
    """)


def downgrade():
    # Drop foreign keys if they exist
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.table_constraints 
                   WHERE table_name = 'wishlists' AND constraint_type = 'FOREIGN KEY') THEN
            ALTER TABLE wishlists DROP CONSTRAINT fk_wishlists_user_id;
        END IF;

        -- Repeat for each foreign key constraint as needed
        -- Replace 'wishlists' and 'fk_wishlists_user_id' with the correct table and constraint names
    END $$;
    """)

    # Drop indexes and table
    op.execute("""
    DROP INDEX IF EXISTS ix_users_username;
    DROP INDEX IF EXISTS ix_users_id;
    DROP INDEX IF EXISTS ix_users_email;
    DROP TABLE IF EXISTS users;
    """)
