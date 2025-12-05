#!/bin/bash

# Navigate to backend directory
cd backend

# Check if chroma_db exists
if [ ! -d "chroma_db" ]; then
    echo "Vector database not found. Starting ingestion..."
    python ingest.py
else
    echo "Vector database found. Skipping ingestion."
fi

# Start the application
echo "Starting FastAPI server..."
# Use --reload for development, remove for production
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
