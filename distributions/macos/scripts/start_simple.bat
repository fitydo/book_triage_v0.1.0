@echo off
echo Starting Book Triage Web Interface (Simple Mode)...
echo.
echo This will start the web server on http://localhost:8000
echo Press Ctrl+C to stop the server when you're done
echo.

REM Change to the project directory
cd /d "%~dp0"

REM Run directly using Python module syntax
echo Starting web server...
python -c "
import sys
sys.path.insert(0, '.')
from book_triage.cli import cli
sys.argv = ['book_triage', 'web', 'sample_books.csv', '--host', '127.0.0.1', '--port', '8000']
cli()
"

echo.
echo Book Triage has stopped.
pause 