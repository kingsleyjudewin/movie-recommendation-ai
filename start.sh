#!/usr/bin/env bash
# CineMind AI — Development startup script (macOS / Linux)
# Starts the FastAPI backend and Vite dev server in background processes.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo " ========================================"
echo "  CineMind AI — starting dev servers..."
echo " ========================================"
echo ""

# Start FastAPI backend
cd "$SCRIPT_DIR"
uvicorn api.main:app --reload --port 8000 &
BACKEND_PID=$!
echo " Backend PID: $BACKEND_PID"

# Start Vite frontend
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!
echo " Frontend PID: $FRONTEND_PID"

echo ""
echo " Backend : http://localhost:8000"
echo " Frontend: http://localhost:8081"
echo ""
echo " Press Ctrl+C to stop both servers."
echo ""

# Wait and clean up on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Servers stopped.'" EXIT
wait
