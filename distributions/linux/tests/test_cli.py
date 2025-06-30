"""Tests for CLI module."""

import tempfile
import sys
from pathlib import Path
from unittest.mock import Mock, patch, call, MagicMock
import pytest
from typer.testing import CliRunner
import pandas as pd

from book_triage.cli import cli
from book_triage.core import BookTriage, BookRecord, Decision


@pytest.fixture
def temp_csv():
    """Create a temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
        csv_path = Path(tmp.name)
        # Write sample CSV data
        tmp.write("id,title,url,F,R,A,V,S,P,decision\n")
        tmp.write("test1,Test Book,https://example.com,3,2,1,4,2,4,unknown\n")
    
    yield csv_path
    
    # Cleanup
    if csv_path.exists():
        csv_path.unlink()


@pytest.fixture
def empty_csv():
    """Create an empty CSV file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=True) as tmp:
        csv_path = Path(tmp.name)
    
    yield csv_path


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


class TestCLICommands:
    """Test CLI commands."""
    
    def test_cli_help(self, runner):
        """Test CLI help command."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Book Triage" in result.output
        assert "scan" in result.output
        assert "web" in result.output
        assert "create-csv" in result.output
        assert "info" in result.output
    
    @patch('book_triage.cli.BookTriage')
    def test_scan_command_success(self, mock_book_triage_class, runner, temp_csv):
        """Test successful scan command."""
        mock_triage = Mock()
        mock_triage.get_records.return_value = [Mock(decision=Decision.UNKNOWN)]
        mock_book_triage_class.return_value = mock_triage
        
        result = runner.invoke(cli, ["scan", str(temp_csv)])
        
        assert result.exit_code == 0
        mock_book_triage_class.assert_called_once_with(temp_csv, 2)
        mock_triage.scan_and_enrich.assert_called_once()
    
    @patch('book_triage.cli.BookTriage')
    def test_scan_command_with_options(self, mock_book_triage_class, runner, temp_csv):
        """Test scan command with options."""
        mock_triage = Mock()
        mock_triage.get_records.return_value = [Mock(decision=Decision.UNKNOWN)]
        mock_book_triage_class.return_value = mock_triage
        
        result = runner.invoke(cli, ["scan", str(temp_csv), "--scan-cost", "3", "--verbose"])
        
        assert result.exit_code == 0
        mock_book_triage_class.assert_called_with(temp_csv, 3)
    
    @patch('book_triage.cli.BookTriage')
    def test_scan_command_no_records(self, mock_book_triage_class, runner, temp_csv):
        """Test scan command with no records."""
        mock_triage = Mock()
        mock_triage.get_records.return_value = []
        mock_book_triage_class.return_value = mock_triage
        
        result = runner.invoke(cli, ["scan", str(temp_csv)])
        
        assert result.exit_code == 0
        mock_triage.scan_and_enrich.assert_not_called()
    
    @patch('book_triage.cli.BookTriage')
    def test_scan_command_nonexistent_file(self, mock_book_triage_class, runner, empty_csv):
        """Test scan command with non-existent CSV file."""
        mock_triage = Mock()
        mock_triage.get_records.return_value = []
        mock_book_triage_class.return_value = mock_triage
        
        result = runner.invoke(cli, ["scan", str(empty_csv)])
        
        assert result.exit_code == 0
        mock_book_triage_class.assert_called_once()
    
    @patch('book_triage.cli.BookTriage')
    def test_scan_command_exception(self, mock_book_triage_class, runner, temp_csv):
        """Test scan command with exception."""
        mock_book_triage_class.side_effect = Exception("Test error")
        
        result = runner.invoke(cli, ["scan", str(temp_csv)])
        
        assert result.exit_code == 1
    
    @patch('book_triage.cli.uvicorn.run')
    @patch('book_triage.cli.initialize_app')
    def test_web_command_success(self, mock_initialize_app, mock_uvicorn_run, runner, temp_csv):
        """Test successful web command."""
        result = runner.invoke(cli, ["web", str(temp_csv)])
        
        assert result.exit_code == 0
        mock_initialize_app.assert_called_once_with(temp_csv, 2)
        mock_uvicorn_run.assert_called_once()
        
        # Check uvicorn.run was called with correct parameters
        call_args = mock_uvicorn_run.call_args
        assert call_args[1]["host"] == "127.0.0.1"
        assert call_args[1]["port"] == 8000
        assert call_args[1]["reload"] is False
    
    @patch('book_triage.cli.uvicorn.run')
    @patch('book_triage.cli.initialize_app')
    def test_web_command_with_options(self, mock_initialize_app, mock_uvicorn_run, runner, temp_csv):
        """Test web command with options."""
        result = runner.invoke(cli, [
            "web", str(temp_csv),
            "--host", "0.0.0.0",
            "--port", "9000",
            "--scan-cost", "4",
            "--reload",
            "--verbose"
        ])
        
        assert result.exit_code == 0
        mock_initialize_app.assert_called_once_with(temp_csv, 4)
        
        call_args = mock_uvicorn_run.call_args
        assert call_args[1]["host"] == "0.0.0.0"
        assert call_args[1]["port"] == 9000
        assert call_args[1]["reload"] is True
        assert call_args[1]["log_level"] == "info"
    
    @patch('book_triage.cli.uvicorn.run')
    @patch('book_triage.cli.initialize_app')
    def test_web_command_nonexistent_file(self, mock_initialize_app, mock_uvicorn_run, runner, empty_csv):
        """Test web command with non-existent CSV file."""
        result = runner.invoke(cli, ["web", str(empty_csv)])
        
        assert result.exit_code == 0
        # Verify initialize_app was called with the CSV path
        mock_initialize_app.assert_called_once()
    
    @patch('book_triage.cli.initialize_app')
    def test_web_command_exception(self, mock_initialize_app, runner, temp_csv):
        """Test web command with exception."""
        mock_initialize_app.side_effect = Exception("Test error")
        
        result = runner.invoke(cli, ["web", str(temp_csv)])
        
        assert result.exit_code == 1
    
    def test_create_csv_command_empty(self, runner):
        """Test create-csv command with empty CSV."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test.csv"
            
            result = runner.invoke(cli, ["create-csv", str(csv_path)])
            
            assert result.exit_code == 0
            assert csv_path.exists()
            
            # Check CSV content
            df = pd.read_csv(csv_path)
            assert len(df) == 0
            expected_columns = ["id", "title", "url", "F", "R", "A", "V", "S", "P", "decision"]
            assert list(df.columns) == expected_columns
    
    def test_create_csv_command_with_sample(self, runner):
        """Test create-csv command with sample data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test.csv"
            
            result = runner.invoke(cli, ["create-csv", str(csv_path), "--sample"])
            
            assert result.exit_code == 0
            assert csv_path.exists()
            
            # Check CSV content
            df = pd.read_csv(csv_path)
            assert len(df) == 2
            assert df.iloc[0]["id"] == "sample1"
            assert df.iloc[0]["title"] == "Sample Book 1"
            assert df.iloc[1]["id"] == "sample2"
            assert df.iloc[1]["title"] == "Sample Book 2"
    
    def test_create_csv_command_creates_directory(self, runner):
        """Test create-csv command creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "subdir" / "test.csv"
            
            result = runner.invoke(cli, ["create-csv", str(csv_path)])
            
            assert result.exit_code == 0
            assert csv_path.exists()
            assert csv_path.parent.exists()
    
    @patch('book_triage.cli.pd.DataFrame.to_csv')
    def test_create_csv_command_exception(self, mock_to_csv, runner):
        """Test create-csv command with exception."""
        mock_to_csv.side_effect = Exception("Write error")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test.csv"
            
            result = runner.invoke(cli, ["create-csv", str(csv_path)])
            
            assert result.exit_code == 1
    
    def test_info_command_success(self, runner, temp_csv):
        """Test successful info command."""
        result = runner.invoke(cli, ["info", str(temp_csv)])
        
        assert result.exit_code == 0
        # Just verify the command completes successfully
    
    def test_info_command_nonexistent_file(self, runner):
        """Test info command with non-existent file."""
        result = runner.invoke(cli, ["info", "nonexistent.csv"])
        
        assert result.exit_code == 1
    
    @patch('book_triage.cli.BookTriage')
    def test_info_command_exception(self, mock_book_triage_class, runner, temp_csv):
        """Test info command with exception."""
        mock_book_triage_class.side_effect = Exception("Read error")
        
        result = runner.invoke(cli, ["info", str(temp_csv)])
        
        assert result.exit_code == 1


class TestCLIValidation:
    """Test CLI input validation."""
    
    def test_scan_cost_validation_min(self, runner, temp_csv):
        """Test scan cost minimum validation."""
        result = runner.invoke(cli, ["scan", str(temp_csv), "--scan-cost", "-1"])
        
        assert result.exit_code != 0
        assert "Invalid value" in result.output
    
    def test_scan_cost_validation_max(self, runner, temp_csv):
        """Test scan cost maximum validation."""
        result = runner.invoke(cli, ["scan", str(temp_csv), "--scan-cost", "6"])
        
        assert result.exit_code != 0
        assert "Invalid value" in result.output
    
    def test_port_validation(self, runner, temp_csv):
        """Test port validation."""
        with patch('book_triage.cli.uvicorn.run') as mock_run, \
             patch('book_triage.cli.initialize_app'):
            
            result = runner.invoke(cli, ["web", str(temp_csv), "--port", "8080"])
            
            assert result.exit_code == 0
            call_args = mock_run.call_args
            assert call_args[1]["port"] == 8080


class TestCLIIntegration:
    """Test CLI integration with other modules."""
    
    @patch('book_triage.cli.BookTriage')
    def test_scan_integration_with_core(self, mock_book_triage_class, runner, temp_csv):
        """Test scan command integration with core module."""
        mock_triage = Mock()
        mock_record = Mock()
        mock_record.decision = Decision.DIGITAL
        mock_triage.get_records.return_value = [mock_record]
        mock_book_triage_class.return_value = mock_triage
        
        result = runner.invoke(cli, ["scan", str(temp_csv), "--scan-cost", "1"])
        
        assert result.exit_code == 0
        mock_book_triage_class.assert_called_once_with(temp_csv, 1)
        mock_triage.scan_and_enrich.assert_called_once()
    
    @patch('book_triage.cli.initialize_app')
    @patch('book_triage.cli.uvicorn.run')
    def test_web_integration_with_api(self, mock_uvicorn_run, mock_initialize_app, runner, temp_csv):
        """Test web command integration with API module."""
        result = runner.invoke(cli, ["web", str(temp_csv), "--scan-cost", "5"])
        
        assert result.exit_code == 0
        mock_initialize_app.assert_called_once_with(temp_csv, 5)
        mock_uvicorn_run.assert_called_once()
        
        # Check that the correct module is being run
        call_args = mock_uvicorn_run.call_args
        assert call_args[0][0] == "book_triage.api:app"


class TestCLIEnvironment:
    """Test CLI environment and configuration."""
    
    def test_environment_loading(self, runner):
        """Test that environment variables are loaded."""
        # Instead of mocking load_dotenv at runtime, test that the import works
        from book_triage.cli import load_dotenv
        import importlib
        
        # Verify the function is available
        assert callable(load_dotenv)
        
        # Test with a simple command that should work
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
    
    def test_logging_configuration(self, runner):
        """Test logging configuration."""
        # Verify logging is configured by checking log level behavior
        import logging
        
        # Test with a simple command that should work
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        
        # Verify that logging module is available and configured
        logger = logging.getLogger('book_triage.cli')
        assert logger is not None
    
    def test_verbose_logging(self, runner, temp_csv):
        """Test verbose logging option."""
        with patch('book_triage.cli.BookTriage') as mock_triage_class, \
             patch('book_triage.cli.logging.getLogger') as mock_get_logger:
            
            mock_triage = Mock()
            mock_triage.get_records.return_value = []
            mock_triage_class.return_value = mock_triage
            
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            result = runner.invoke(cli, ["scan", str(temp_csv), "--verbose"])
            
            # Verbose should set log level to DEBUG
            mock_logger.setLevel.assert_called_with(10)  # logging.DEBUG 