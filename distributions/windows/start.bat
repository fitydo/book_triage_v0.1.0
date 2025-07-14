@echo off
title Book Triage - Starting...

echo ============================================================
echo                    Book Triage Startup
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Use examples\sample_books.csv if it exists, otherwise create books.csv
if exist "examples\sample_books.csv" (
    echo Using existing examples\sample_books.csv with sample data
    set CSV_FILE=examples\sample_books.csv
) else (
    if not exist "books.csv" (
        echo Creating new books.csv file...
        echo id,title,isbn,url,url_com,purchase_price,used_price,F,A,S,V,R,P,citation_R,citation_P,decision,verified > books.csv
        echo Created new books.csv file
    )
    set CSV_FILE=books.csv
)

echo Starting Book Triage Web Interface...
echo.
echo The web interface will open at: http://localhost:8000
echo Your default web browser will open automatically in a few seconds.
echo.
echo Instructions:
echo - Upload book photos to extract titles automatically
echo - Add manual entries with ISBN numbers
echo - Click "Scan & Enrich" to get pricing and recommendations
echo - View your book collection and decisions
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Start the web interface with the CSV file
python -m book_triage.cli web "%CSV_FILE%" --port 8000 --host 127.0.0.1

REM If the above fails, pause to see the error
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start Book Triage
    echo Please check that all dependencies are installed
    pause
)
