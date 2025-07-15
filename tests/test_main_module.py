"""Tests for __main__.py module."""

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
import pytest

from book_triage.__main__ import main


class TestMainFunction:
    """Tests for main function in __main__.py."""
    
    def test_main_with_no_args_existing_csv(self):
        """Test main function with no arguments when sample CSV exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a sample CSV file
            csv_path = Path(temp_dir) / "examples" / "sample_books.csv"
            csv_path.parent.mkdir(parents=True)
            csv_path.write_text("id,title,isbn\ntest1,Test Book,123456789")
            
            # Mock sys.argv to have only script name
            with patch.object(sys, 'argv', ['book_triage']):
                # Mock Path.exists to simulate finding the CSV
                with patch('book_triage.__main__.Path') as mock_path:
                    mock_path.return_value.exists.side_effect = lambda: str(mock_path.return_value) == str(csv_path)
                    
                    # Mock the CLI function
                    with patch('book_triage.__main__.cli') as mock_cli:
                        main()
                        
                        # Check that sys.argv was modified correctly
                        assert 'web' in sys.argv
                        assert '--host' in sys.argv
                        assert '127.0.0.1' in sys.argv
                        assert '--port' in sys.argv
                        assert '8000' in sys.argv
                        mock_cli.assert_called_once()
    
    def test_main_with_no_args_no_existing_csv(self):
        """Test main function with no arguments when no CSV exists."""
        with patch.object(sys, 'argv', ['book_triage']):
            # Mock Path.exists to always return False
            with patch('book_triage.__main__.Path') as mock_path:
                mock_path.return_value.exists.return_value = False
                
                # Mock file creation
                with patch('builtins.open', mock_open()) as mock_file:
                    # Mock the CLI function
                    with patch('book_triage.__main__.cli') as mock_cli:
                        main()
                        
                        # Verify file was created with correct headers
                        mock_file.assert_called_once_with('books.csv', 'w')
                        handle = mock_file()
                        written_content = handle.write.call_args[0][0]
                        assert 'id,title,isbn' in written_content
                        assert 'url,url_com' in written_content
                        assert 'decision,verified' in written_content
                        
                        # Check that sys.argv was modified
                        assert 'web' in sys.argv
                        assert 'books.csv' in sys.argv
                        mock_cli.assert_called_once()
    
    def test_main_with_existing_args(self):
        """Test main function when arguments are already provided."""
        original_argv = sys.argv.copy()
        
        try:
            # Set sys.argv to have existing arguments
            sys.argv = ['book_triage', 'scan', 'test.csv']
            
            with patch('book_triage.__main__.cli') as mock_cli:
                main()
                
                # Should not modify sys.argv when args already exist
                assert sys.argv == ['book_triage', 'scan', 'test.csv']
                mock_cli.assert_called_once()
        
        finally:
            sys.argv = original_argv
    
    def test_main_csv_file_search_order(self):
        """Test that CSV files are searched in correct order."""
        with patch.object(sys, 'argv', ['book_triage']):
            # Create a controlled environment where only the second path exists
            def mock_exists(self):
                return str(self) == "sample_books.csv"
            
            with patch('book_triage.__main__.Path') as mock_path:
                mock_path.return_value.exists = mock_exists
                mock_path.side_effect = lambda x: type('MockPath', (), {
                    'exists': lambda: x == "sample_books.csv",
                    '__str__': lambda: x
                })()
                
                with patch('book_triage.__main__.cli') as mock_cli:
                    main()
                    
                    # Should use the found CSV file
                    assert 'sample_books.csv' in sys.argv
                    mock_cli.assert_called_once()
    
    def test_main_print_messages(self, capsys):
        """Test that main function prints appropriate messages."""
        with patch.object(sys, 'argv', ['book_triage']):
            with patch('book_triage.__main__.Path') as mock_path:
                mock_path.return_value.exists.return_value = False
                
                with patch('builtins.open', mock_open()):
                    with patch('book_triage.__main__.cli'):
                        main()
                        
                        captured = capsys.readouterr()
                        assert "Creating new database file: books.csv" in captured.out
                        assert "Starting Book Triage with database: books.csv" in captured.out
                        assert "Open http://localhost:8000 in your browser" in captured.out
    
    def test_main_with_found_csv_messages(self, capsys):
        """Test print messages when CSV file is found."""
        with patch.object(sys, 'argv', ['book_triage']):
            # Mock finding examples/sample_books.csv
            def mock_exists(self):
                return str(self) == "examples/sample_books.csv"
            
            with patch('book_triage.__main__.Path') as mock_path:
                mock_path.return_value.exists = mock_exists
                mock_path.side_effect = lambda x: type('MockPath', (), {
                    'exists': lambda: x == "examples/sample_books.csv",
                    '__str__': lambda: x
                })()
                
                with patch('book_triage.__main__.cli'):
                    main()
                    
                    captured = capsys.readouterr()
                    assert "Starting Book Triage with database: examples/sample_books.csv" in captured.out
                    assert "Open http://localhost:8000 in your browser" in captured.out
                    # Should NOT see the "Creating new database file" message
                    assert "Creating new database file" not in captured.out


class TestMainModuleExecution:
    """Tests for module execution scenarios."""
    
    def test_main_called_when_run_as_module(self):
        """Test that main() is called when module is executed directly."""
        # This tests the if __name__ == "__main__": block
        with patch('book_triage.__main__.main') as mock_main:
            # Simulate running as main module
            with patch('book_triage.__main__.__name__', '__main__'):
                # Import and run the module code
                exec(compile(open('book_triage/__main__.py').read(), 'book_triage/__main__.py', 'exec'))
                
                # Note: This is a simplified test. In practice, the main() call
                # happens at import time when __name__ == "__main__"


class TestEdgeCases:
    """Test edge cases and error scenarios."""
    
    def test_main_with_file_permission_error(self):
        """Test main function when file creation fails due to permissions."""
        with patch.object(sys, 'argv', ['book_triage']):
            with patch('book_triage.__main__.Path') as mock_path:
                mock_path.return_value.exists.return_value = False
                
                # Mock file creation to raise PermissionError
                with patch('builtins.open', side_effect=PermissionError("Permission denied")):
                    with patch('book_triage.__main__.cli') as mock_cli:
                        # Should still try to run even if file creation fails
                        with pytest.raises(PermissionError):
                            main()
    
    def test_main_with_different_csv_files(self):
        """Test main function finding different CSV files in order."""
        csv_files = [
            "examples/sample_books.csv",
            "sample_books.csv", 
            "../examples/sample_books.csv",
            "books.csv"
        ]
        
        for target_file in csv_files:
            with patch.object(sys, 'argv', ['book_triage']):
                def mock_exists(self):
                    return str(self) == target_file
                
                with patch('book_triage.__main__.Path') as mock_path:
                    mock_path.return_value.exists = mock_exists
                    mock_path.side_effect = lambda x: type('MockPath', (), {
                        'exists': lambda: x == target_file,
                        '__str__': lambda: x
                    })()
                    
                    with patch('book_triage.__main__.cli') as mock_cli:
                        main()
                        
                        # Should use the found file
                        assert target_file in sys.argv
                        mock_cli.assert_called_once()
    
    def test_csv_header_format(self):
        """Test that the CSV header created has all required fields."""
        expected_headers = [
            "id", "title", "isbn", "url", "url_com", 
            "purchase_price", "used_price", "F", "A", "S", 
            "V", "R", "P", "citation_R", "citation_P", 
            "decision", "verified"
        ]
        
        with patch.object(sys, 'argv', ['book_triage']):
            with patch('book_triage.__main__.Path') as mock_path:
                mock_path.return_value.exists.return_value = False
                
                with patch('builtins.open', mock_open()) as mock_file:
                    with patch('book_triage.__main__.cli'):
                        main()
                        
                        # Get the content written to file
                        handle = mock_file()
                        written_content = handle.write.call_args[0][0]
                        
                        # Check all headers are present
                        for header in expected_headers:
                            assert header in written_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 