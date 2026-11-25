#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Starting TidyTrack Backend on port 8000..."
cd "$DIR/backend"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "Starting TidyTrack Frontend on port 5173..."
cd "$DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo "TidyTrack is running!"
echo "  Backend:  http://localhost:8000 (docs: http://localhost:8000/docs)"
echo "  Frontend: http://localhost:5173"
echo "Press Ctrl+C to stop both servers."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT INT TERM
wait
