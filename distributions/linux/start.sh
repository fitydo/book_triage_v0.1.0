#!/bin/bash

echo "============================================================"
echo "                    Book Triage Startup"
echo "============================================================"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Use examples/sample_books.csv if it exists, otherwise create books.csv
if [ -f "examples/sample_books.csv" ]; then
    echo "Using existing examples/sample_books.csv with sample data"
    CSV_FILE="examples/sample_books.csv"
else
    if [ ! -f "books.csv" ]; then
        echo "Creating new books.csv file..."
        echo "id,title,isbn,url,url_com,purchase_price,used_price,F,A,S,V,R,P,citation_R,citation_P,decision,verified" > books.csv
        echo "Created new books.csv file"
    fi
    CSV_FILE="books.csv"
fi

echo "Starting Book Triage Web Interface..."
echo
echo "The web interface will open at: http://localhost:8000"
echo
echo "Instructions:"
echo "- Upload book photos to extract titles automatically"
echo "- Add manual entries with ISBN numbers"
echo "- Click 'Scan & Enrich' to get pricing and recommendations"
echo "- View your book collection and decisions"
echo
echo "Press Ctrl+C to stop the server"
echo "============================================================"
echo

# Start the web interface with the CSV file
python3 -m book_triage.cli web "$CSV_FILE" --port 8000 --host 127.0.0.1
