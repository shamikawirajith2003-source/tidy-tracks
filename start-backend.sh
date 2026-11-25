#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR/backend"
echo "Starting TidyTrack Backend on http://localhost:8000..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
