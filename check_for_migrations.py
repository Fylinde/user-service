from sqlalchemy import create_engine
from alembic.migration import MigrationContext
from alembic.operations import Operations
from app.database import BaseModel  # Import your base model class
from app.models import *  # Import all your models
from sqlalchemy.schema import MetaData
from sqlalchemy import inspect

def compare_metadata(metadata, engine):
    inspector = inspect(engine)
    current_tables = set(inspector.get_table_names())
    metadata_tables = set(metadata.tables.keys())
    
    # Check if any tables are in the metadata but not in the database
    missing_tables = metadata_tables - current_tables
    extra_tables = current_tables - metadata_tables

    # Check for differences in existing tables
    diffs = []
    
    for table_name in metadata_tables.intersection(current_tables):
        metadata_table = metadata.tables[table_name]
        db_columns = inspector.get_columns(table_name)
        db_column_names = set(col['name'] for col in db_columns)
        metadata_column_names = set(metadata_table.columns.keys())
        
        # Find missing or extra columns
        missing_columns = metadata_column_names - db_column_names
        extra_columns = db_column_names - metadata_column_names
        
        if missing_columns or extra_columns:
            diffs.append({
                'table': table_name,
                'missing_columns': missing_columns,
                'extra_columns': extra_columns
            })
    
    return diffs, missing_tables, extra_tables

def check_for_migrations(database_url):
    # Create the database engine
    engine = create_engine(database_url)

    # Get the metadata of your models
    current_metadata = BaseModel.metadata

    # Compare the metadata from the code with the database schema
    diffs, missing_tables, extra_tables = compare_metadata(current_metadata, engine)
    
    if not diffs and not missing_tables and not extra_tables:
        print("No migrations are needed. The database schema is up-to-date.")
    else:
        print("Migrations are needed. The following differences were found:")
        if missing_tables:
            print(f"Missing tables in the database: {missing_tables}")
        if extra_tables:
            print(f"Extra tables in the database: {extra_tables}")
        for diff in diffs:
            print(f"Table '{diff['table']}' has missing columns: {diff['missing_columns']} and extra columns: {diff['extra_columns']}")

    # Clean up the connection
    engine.dispose()

if __name__ == "__main__":
    # Replace with your actual database URL
    database_url = "postgresql+psycopg2://postgres:Sylvian@db:5433/user_service_db"
    check_for_migrations(database_url)
