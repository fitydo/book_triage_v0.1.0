"""Main entry point for book_triage module."""

import sys
import os
from pathlib import Path
from .cli import cli

def main():
    """Main function with default behavior for no arguments."""
    # If no arguments provided, start web interface with default CSV
    if len(sys.argv) == 1:
        # Look for sample_books.csv in various locations
        possible_paths = [
            Path("examples/sample_books.csv"),
            Path("sample_books.csv"),
            Path("../examples/sample_books.csv"),
            Path("books.csv")
        ]
        
        csv_file = None
        for path in possible_paths:
            if path.exists():
                csv_file = str(path)
                break
        
        # If no existing CSV found, create a new one
        if not csv_file:
            csv_file = "books.csv"
            print(f"Creating new database file: {csv_file}")
            with open(csv_file, 'w') as f:
                f.write("id,title,isbn,url,url_com,purchase_price,used_price,F,A,S,V,R,P,citation_R,citation_P,decision,verified\n")
        
        # Add default web command arguments
        sys.argv.extend(['web', csv_file, '--host', '127.0.0.1', '--port', '8000'])
        print(f"Starting Book Triage with database: {csv_file}")
        print("Open http://localhost:8000 in your browser")
    
    # Run the CLI
    cli()

if __name__ == "__main__":
    main() 