#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Ensuring virtual environment and dependencies are up to date with uv..."
# Create a virtual environment if it doesn't exist, and sync dependencies.
# This single command handles both creation and synchronization.
uv pip sync pyproject.toml

echo "Starting Redis server in the background..."
redis-server --daemonize yes

echo "Starting FastAPI server in the background..."
# Use 'uv run' to execute commands within the managed environment
uv run uvicorn app.api.main:app --host 127.0.0.1 --port 8000 > fastapi.log 2>&1 &
API_PID=$!
echo "FastAPI server started with PID $API_PID. Logs in fastapi.log"

echo "Starting RQ worker in the background..."
uv run rq worker --url redis://localhost:6379 > worker.log 2>&1 &
WORKER_PID=$!
echo "RQ worker started with PID $WORKER_PID. Logs in worker.log"

echo "Starting Streamlit UI in the foreground..."
# Wait for the API to be ready before starting Streamlit
sleep 5
uv run streamlit run streamlit_app/app.py

# Clean up background jobs when Streamlit is closed
echo "Streamlit closed, shutting down background processes..."
kill $API_PID
kill $WORKER_PID
redis-cli shutdown
echo "Shutdown complete." 