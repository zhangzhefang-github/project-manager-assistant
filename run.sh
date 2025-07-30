#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Ensuring virtual environment and dependencies are up to date with uv..."
uv sync

# Use a logs directory
mkdir -p logs

# Start FastAPI server in the background, redirecting stdout and stderr to a log file
echo "Starting FastAPI server in the background..."
uv run uvicorn app.api.main:app --host 0.0.0.0 --port 8000 > logs/fastapi.log 2>&1 &
API_PID=$!
echo "FastAPI server started with PID $API_PID. Logs in logs/fastapi.log"

# Start RQ worker in the background, redirecting stdout and stderr to a log file
echo "Starting RQ worker in the background..."
uv run rq worker --url redis://localhost:6379 > logs/worker.log 2>&1 &
WORKER_PID=$!
echo "RQ worker started with PID $WORKER_PID. Logs in logs/worker.log"

# Start Streamlit UI in the foreground. Its logs will appear directly in the console.
echo "Starting Streamlit UI in the foreground..."
sleep 3 # Give backend a moment to start
uv run streamlit run streamlit_app/app.py

# --- Cleanup ---
# This part runs when the user closes Streamlit (Ctrl+C)
echo "Streamlit closed, shutting down background processes..."
kill $API_PID || true # Use '|| true' to prevent script from exiting if process is already gone
kill $WORKER_PID || true
echo "Shutdown complete. You may need to stop the Redis Docker container manually." 