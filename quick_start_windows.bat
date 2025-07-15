@echo off
echo.
echo ========================================
echo   Book Triage - Windows Quick Start
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "pyproject.toml" (
    echo Error: pyproject.toml not found. Please run this from the book_triage_v0.1.0 directory.
    pause
    exit /b 1
)

echo Step 1: Creating environment file...
echo.

REM Create .env file if it doesn't exist
if not exist ".env" (
    powershell -Command "Set-Content -Path '.env' -Value @('# Book Triage Environment Configuration','#','# Basic Authentication (Required for web interface)','BOOK_USER=admin','BOOK_PASS=password','#','# OpenAI API Key (Optional - for advanced OCR features)','# Get your key from: https://platform.openai.com/api-keys','# OPENAI_API_KEY=your_openai_key_here') -Encoding UTF8"
    echo.
    echo ✅ Created .env file with default settings (UTF-8 encoding)
) else (
    echo ✅ .env file already exists
)

echo.
echo Step 2: Creating sample data...
python -m book_triage create-csv books.csv --sample
if %errorlevel% neq 0 (
    echo ❌ Failed to create sample data
    pause
    exit /b 1
)

echo.
echo Step 3: Starting web interface...
echo.
echo 🌐 Book Triage will start at: http://localhost:8000
echo 🔐 Login with: admin / password
echo.
echo ⚠️  Note: OCR features require OpenAI API key in .env file
echo 📝 Edit .env file to add your OpenAI API key for full functionality
echo.
echo Starting server... (Press Ctrl+C to stop)
echo.

python -m book_triage web books.csv

echo.
echo Server stopped.
pause 