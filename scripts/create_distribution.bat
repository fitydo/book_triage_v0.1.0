@echo off
echo Creating Book Triage Distribution Package...
echo.

REM Create distribution folder
if exist "book_triage_distribution" rmdir /s /q "book_triage_distribution"
mkdir "book_triage_distribution"

REM Copy essential files
echo Copying app files...
xcopy /s /e "book_triage" "book_triage_distribution\book_triage\"
copy "pyproject.toml" "book_triage_distribution\"
copy "README.md" "book_triage_distribution\"
copy "sample_books.csv" "book_triage_distribution\"
copy ".env.example" "book_triage_distribution\"
copy "start_book_triage.bat" "book_triage_distribution\"
copy "start_simple.bat" "book_triage_distribution\"
copy "start_book_triage.ps1" "book_triage_distribution\"
copy "SETUP_INSTRUCTIONS.md" "book_triage_distribution\"

REM Copy tests (optional)
xcopy /s /e "tests" "book_triage_distribution\tests\"

echo.
echo ✅ Distribution package created in 'book_triage_distribution' folder
echo.
echo 📦 Ready to share:
echo    - Zip the 'book_triage_distribution' folder
echo    - Or copy the folder to USB/cloud storage
echo    - Recipients follow SETUP_INSTRUCTIONS.md
echo.
pause 