#!/usr/bin/env pwsh

Write-Host "Starting Book Triage Web Interface..." -ForegroundColor Green
Write-Host ""
Write-Host "This will start the web server on http://localhost:8000" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server when you're done" -ForegroundColor Yellow
Write-Host ""

# Change to the script directory
Set-Location $PSScriptRoot

try {
    # First install the package in development mode
    Write-Host "Installing/updating book_triage package..." -ForegroundColor Cyan
    pip install -e .
    
    Write-Host ""
    Write-Host "Starting web server..." -ForegroundColor Cyan
    
    # Start the web interface with sample_books.csv
    python -m book_triage.cli web sample_books.csv --host 127.0.0.1 --port 8000
}
catch {
    Write-Host "Error starting Book Triage: $_" -ForegroundColor Red
}
finally {
    Write-Host ""
    Write-Host "Book Triage has stopped." -ForegroundColor Green
    Read-Host "Press Enter to close this window"
} 