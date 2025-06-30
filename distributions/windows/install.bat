@echo off
echo Book Triage Windows Installation
echo ================================
echo.
echo Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -e .
echo.
echo Setup complete!
echo To start: python -m uvicorn book_triage.api:app --reload
echo.
pause
