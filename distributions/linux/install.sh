#!/bin/bash
echo "Book Triage Linux Installation"
echo "=============================="
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.12+"
    exit 1
fi

echo "Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y python3-pip libmagic1 tesseract-ocr
elif command -v yum &> /dev/null; then
    sudo yum install -y python3-pip file-devel tesseract
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
