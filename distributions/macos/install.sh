#!/bin/bash
echo "Book Triage macOS Installation"
echo "=============================="
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.12+"
    exit 1
fi

echo "Installing dependencies..."
if command -v brew &> /dev/null; then
    brew install libmagic tesseract
else
    echo "Warning: Homebrew not found. Install manually:"
    echo "  libmagic and tesseract"
fi

echo "Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -e .

echo
echo "Setup complete!"
echo "To start: python3 -m book_triage"
echo "Or run: ./start.sh"
echo "Web interface will be at http://localhost:8000"
echo
