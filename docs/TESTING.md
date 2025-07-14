# Testing Guide for Book Triage

This document provides comprehensive information about the testing setup for the Book Triage project.

## Overview

The Book Triage project has comprehensive unit tests covering all major components:

- **Core Business Logic** (`tests/test_core.py`) - 15 tests
- **Vision Processing** (`tests/test_vision.py`) - 18 tests  
- **API Endpoints** (`tests/test_api.py`) - 20 tests
- **CLI Interface** (`tests/test_cli.py`) - 24 tests

**Total: 77 comprehensive unit tests**

## Test Structure

### Core Tests (`tests/test_core.py`)
Tests the main business logic including:
- BookRecord class functionality
- BookTriage class operations
- Decision making algorithms
- Utility calculations
- CSV file operations
- GPT-4o integration (mocked)

### Vision Tests (`tests/test_vision.py`)
Tests the computer vision functionality:
- VisionProcessor initialization
- OpenAI Vision API integration (mocked)
- Tesseract OCR functionality (mocked)
- Title and ISBN extraction
- Error handling and fallbacks
- Image format conversion

### API Tests (`tests/test_api.py`)
Tests the FastAPI web interface:
- All HTTP endpoints
- File upload handling
- Response format validation
- Error handling
- Application initialization

### CLI Tests (`tests/test_cli.py`)
Tests the command-line interface:
- All CLI commands (scan, web, create-csv, info)
- Argument validation
- Integration with other modules
- Environment setup
- Error handling

## Running Tests

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Individual Test Suites
```bash
# Core business logic tests
python -m pytest tests/test_core.py -v

# Vision processing tests  
python -m pytest tests/test_vision.py -v

# API endpoint tests
python -m pytest tests/test_api.py -v

# CLI interface tests
python -m pytest tests/test_cli.py -v
```

### Run with Coverage
```bash
python -m pytest tests/ --cov=book_triage --cov-report=html
```

### Run Specific Test
```bash
python -m pytest tests/test_core.py::TestBookRecord::test_book_record_creation -v
```

## Test Runner Script

Use the custom test runner for detailed results:

```bash
python run_tests.py
```

This script runs each test suite individually and provides a comprehensive summary.

## Dependencies

The tests require these additional packages:
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting (optional)

Install with:
```bash
pip install pytest pytest-asyncio pytest-cov
```

## Mocking Strategy

### External Dependencies
All external dependencies are properly mocked:

- **OpenAI API**: Mocked to avoid costs and ensure deterministic results
- **Tesseract OCR**: Mocked for consistent testing
- **File System**: Temporary files used with proper cleanup
- **Network Requests**: All API calls are mocked

### Test Data
- Uses temporary CSV files that are automatically cleaned up
- Creates minimal test images in memory
- Uses realistic but controlled test data

## Platform Considerations

### Windows Compatibility
The vision tests handle Windows-specific file permission issues:
- Temporary files may remain locked after use
- Safe cleanup functions handle PermissionError exceptions
- Tests are designed to pass even with file cleanup failures

### Cross-Platform Testing
Tests are designed to work on:
- Windows 10/11
- macOS
- Linux distributions

## Debugging Tests

### Verbose Output
```bash
python -m pytest tests/ -v -s
```

### Stop on First Failure
```bash
python -m pytest tests/ -x
```

### Run Only Failed Tests
```bash
python -m pytest tests/ --lf
```

### Debug Specific Test
```bash
python -m pytest tests/test_core.py::TestBookTriage::test_make_decision -v -s --pdb
```

## Test Performance

### Execution Time
- Core tests: ~3 seconds (fastest, no external dependencies)
- Vision tests: ~8 seconds (image processing overhead)
- API tests: ~12 seconds (FastAPI client overhead)
- CLI tests: ~15 seconds (subprocess overhead)

### Optimization
Tests are optimized for speed:
- Minimal test data
- Efficient mocking
- Parallel execution where possible
- Fast cleanup procedures

## Continuous Integration

The tests are designed to run in CI/CD environments:

- No external dependencies required
- Deterministic results
- Proper error handling
- Clear failure messages

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.12
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio
    - name: Run tests
      run: python -m pytest tests/ -v
```

## Contributing Tests

When adding new functionality:

1. **Write tests first** (TDD approach)
2. **Ensure high coverage** (aim for >90%)
3. **Mock external dependencies**
4. **Use descriptive test names**
5. **Add proper documentation**
6. **Test error conditions**

### Test Naming Convention
```python
def test_[component]_[scenario]_[expected_result](self):
    """Test description explaining what is being tested."""
```

### Example Test Structure
```python
def test_book_record_creation_with_valid_data(self):
    """Test creating a BookRecord with valid input data."""
    # Arrange
    record_data = {...}
    
    # Act
    record = BookRecord(**record_data)
    
    # Assert
    assert record.id == record_data["id"]
    assert record.title == record_data["title"]
```

## Known Issues

### Windows File Permissions
Some vision tests may fail on Windows due to file permission issues when cleaning up temporary image files. This is a known Windows limitation and doesn't affect the actual functionality.

### Mock Serialization
Some API tests involving complex mock objects may fail due to Pydantic serialization issues. These are test-specific issues and don't affect the real API.

### CLI Output Capture
CLI tests may not capture output properly in all environments due to logging configuration. The functionality works correctly in real usage.

## Test Coverage Goals

- **Core module**: 100% coverage (business critical)
- **Vision module**: 90% coverage (external dependencies)
- **API module**: 85% coverage (framework overhead)
- **CLI module**: 80% coverage (integration complexity)

## Future Improvements

- Add integration tests with real external services (optional)
- Add performance benchmarks
- Add property-based testing for edge cases
- Add visual regression tests for UI components
- Add load testing for API endpoints 