@echo off
echo Book Triage Windows Installation
echo ================================
echo.
echo Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -e .
echo.
echo Setup complete!
echo.
echo To start Book Triage:
echo   1. Double-click 'book_triage.bat' or 'start.bat'
echo   2. Or run: python -m book_triage
echo.
echo The web interface will open at http://localhost:8000
echo.
pause
