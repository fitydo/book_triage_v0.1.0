# Directory Structure

This document describes the organized directory structure of the Book Triage project.

## Root Directory

The root directory now contains only essential project files:

- `README.md` - Main project documentation
- `LICENSE` - Project license
- `requirements.txt` - Python dependencies
- `pyproject.toml` - Python project configuration
- `CONTRIBUTING.md` - Contribution guidelines
- `.gitignore` - Git ignore rules

## Core Directories

### `/book_triage/`
Main application source code

### `/tests/`
Unit tests and test utilities

### `/scripts/`
Utility scripts for development and deployment

### `/examples/`
Example files and sample data

### `/distributions/`
Platform-specific distribution files

### `/.github/`
GitHub workflows and CI/CD configuration

## Documentation

### `/docs/`
All documentation files including:
- Installation guides (`INSTALL_WINDOWS.md`, `quick_start_windows.bat`)
- Setup instructions (`QUICK_SETUP.md`, `SETUP_INSTRUCTIONS.md`)
- Security documentation (`SECURITY_ANALYSIS.md`, `SECURITY_CHECKLIST.md`)
- Testing documentation (`TESTING.md`, `UNIT_TEST_SUMMARY.md`)
- Performance reports (`PERFORMANCE_SUMMARY.md`)
- UML diagrams (`/uml/`)
- Architecture decision records (`/adr/`)

## Development Files

### `/test_data/`
Test CSV files and sample data:
- `books.csv` - Sample book database
- `test_sample*.csv` - Various test datasets

### `/temp_files/`
Temporary and development files:
- `.coverage` - Test coverage reports
- `test_web_interface.html` - Web interface testing
- `test_installation.py` - Installation testing
- `compatibility_test_windows.txt` - Windows compatibility tests

## Hidden Directories

### `/.git/`
Git version control data

### `/.pytest_cache/`
Pytest cache files

## File Organization Principles

1. **Root directory** - Only essential project files
2. **Source code** - Organized in logical modules
3. **Documentation** - Centralized in `/docs/`
4. **Test data** - Separated from source code
5. **Temporary files** - Isolated for easy cleanup
6. **Platform-specific** - Organized by distribution target 