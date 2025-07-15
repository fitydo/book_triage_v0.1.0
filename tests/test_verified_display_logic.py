#!/usr/bin/env python3
"""Check that the served HTML uses strict equality for verified display."""

import re
import subprocess
import time
import urllib.request
from pathlib import Path
from book_triage.core import BookTriage, BookRecord
import uvicorn
import multiprocessing

PORT = 8123
CSV_PATH = Path(__file__).parent / "_tmp_books.csv"

def start_server():
    BookTriage(CSV_PATH)  # ensure file exists
    uvicorn.run("book_triage.api:app", host="127.0.0.1", port=PORT, log_level="error")

def test_verified_column_uses_strict_equality():
    # create minimal csv
    CSV_PATH.write_text("id,title,decision,verified\nabc,Test Book,unknown,no\n")

    proc = multiprocessing.Process(target=start_server, daemon=True)
    proc.start()
    try:
        time.sleep(1.5)  # give server time
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}") as response:
            html = response.read().decode('utf-8')
        # Ensure strict equality JS is present
        assert "book.verified === 'yes' ? 'Yes' : 'No'" in html
    finally:
        proc.terminate()
        if CSV_PATH.exists():
            CSV_PATH.unlink() 