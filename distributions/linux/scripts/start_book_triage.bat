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

echo Python found - checking dependencies...

REM Install the package in development mode
echo Installing Book Triage package...
pip install -e . >nul 2>&1
if errorlevel 1 (
    echo WARNING: Could not install package in development mode
    echo You may need to run: pip install -e .
    echo.
)

REM Install dependencies
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo WARNING: Could not install dependencies automatically
    echo You may need to run: pip install -r requirements.txt
    echo.
)

REM Use sample_books.csv if it exists, otherwise create books.csv
if exist "sample_books.csv" (
    echo Using existing sample_books.csv with sample data
    set CSV_FILE=sample_books.csv
) else (
    if not exist "books.csv" (
        echo id,title,isbn,url,url_com,purchase_price,used_price,F,A,S,V,decision > books.csv
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

REM Start the web interface with default settings
start /b python -m book_triage.cli web %CSV_FILE% --port 8000 --host 127.0.0.1

REM Wait a moment for the server to start
timeout /t 2 /nobreak >nul

REM Automatically open the web browser
echo Opening web browser...
start http://localhost:8000

echo.
echo Server is running. Press Ctrl+C in this window to stop the server.
pause 