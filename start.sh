#!/bin/bash

echo "Starting start.sh script..."

# Ensure the wait-for-it script is executable
chmod +x ./wait-for-it.sh
echo "wait-for-it.sh script is now executable."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL server to be available..."
./wait-for-it.sh db:5432 --timeout=180 --strict -- \
    echo "PostgreSQL is up - executing command"

# Run Alembic migrations
echo "Running database migrations..."
alembic upgrade head

# Start the FastAPI application with Uvicorn
echo "Starting user-service..."
uvicorn main:app --host 0.0.0.0 --port 8001
