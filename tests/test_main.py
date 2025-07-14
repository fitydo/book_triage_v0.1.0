"""Tests for book_triage.__main__ module."""

import sys
import os
from pathlib import Path
import pytest
from unittest.mock import patch, mock_open, MagicMock
import tempfile
import shutil

from book_triage.__main__ import main


class TestMainModule:
    """Test cases for the __main__ module."""
    
    def setup_method(self):
        """Set up test environment."""
        # Save original sys.argv
        self.original_argv = sys.argv.copy()
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        # Restore original sys.argv
        sys.argv = self.original_argv
        # Restore original working directory and clean up
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    def test_main_no_args_with_existing_csv(self):
        """Test main function with no arguments when sample CSV exists."""
        # Create examples directory and sample CSV
        os.makedirs("examples", exist_ok=True)
        sample_csv = Path("examples/sample_books.csv")
        sample_csv.write_text("id,title,isbn,url\n1,Test Book,123,http://test.com\n")
        
        # Mock sys.argv and cli
        sys.argv = ["book_triage"]
        
        with patch("book_triage.__main__.cli") as mock_cli:
            main()
            
            # Check that sys.argv was extended with web command
            # Handle platform-specific path separators
            expected_path = str(Path("examples/sample_books.csv"))
            assert sys.argv == ["book_triage", "web", expected_path, 
                              "--host", "127.0.0.1", "--port", "8000"]
            mock_cli.assert_called_once()
    
    def test_main_no_args_creates_new_csv(self):
        """Test main function creates new CSV when none exists."""
        # Ensure no CSV files exist
        sys.argv = ["book_triage"]
        
        with patch("book_triage.__main__.cli") as mock_cli:
            main()
            
            # Check that books.csv was created
            assert Path("books.csv").exists()
            content = Path("books.csv").read_text()
            assert "id,title,isbn,url,url_com,purchase_price" in content
            
            # Check that sys.argv was extended
            assert sys.argv == ["book_triage", "web", "books.csv", 
                              "--host", "127.0.0.1", "--port", "8000"]
            mock_cli.assert_called_once()
    
    def test_main_with_args(self):
        """Test main function with command line arguments."""
        # Set up sys.argv with arguments
        sys.argv = ["book_triage", "scan", "test.csv"]
        
        with patch("book_triage.__main__.cli") as mock_cli:
            main()
            
            # Check that sys.argv was not modified
            assert sys.argv == ["book_triage", "scan", "test.csv"]
            mock_cli.assert_called_once()
    
    def test_main_finds_alternative_csv_paths(self):
        """Test main function finds CSV in alternative locations."""
        # Create sample_books.csv in current directory
        sample_csv = Path("sample_books.csv")
        sample_csv.write_text("id,title\n1,Book\n")
        
        sys.argv = ["book_triage"]
        
        with patch("book_triage.__main__.cli") as mock_cli:
            main()
            
            # Should find sample_books.csv in current directory
            assert sys.argv == ["book_triage", "web", "sample_books.csv", 
                              "--host", "127.0.0.1", "--port", "8000"]
            mock_cli.assert_called_once()
    
    def test_main_module_entry_point(self):
        """Test the if __name__ == '__main__' entry point."""
        # This tests the module-level code
        with patch("book_triage.__main__.main") as mock_main:
            # Import and execute the module
            import book_triage.__main__
            # The main() should not be called during import
            mock_main.assert_not_called() 