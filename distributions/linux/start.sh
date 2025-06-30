#!/bin/bash
echo "Starting Book Triage..."
echo "Open browser to: http://localhost:8000"
python3 -m uvicorn book_triage.api:app --host 0.0.0.0 --port 8000
