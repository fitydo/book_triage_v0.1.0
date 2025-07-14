# Contributing to Book Triage

Thank you for your interest in contributing to Book Triage! This guide will help you get started with contributing to our cross-platform book management tool.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Issue Management](#issue-management)
- [Branch Strategy](#branch-strategy)
- [Documentation](#documentation)
- [Release Process](#release-process)

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct. Please be respectful, inclusive, and constructive in all interactions.

## Getting Started

### Prerequisites

- **Python 3.12+** (required)
- **Git** for version control
- **Poetry** (recommended) or pip for dependency management
- **Platform-specific dependencies**:
  - **Windows**: Python magic binary (`python-magic-bin`)
  - **Linux**: `libmagic1`, `tesseract-ocr` (`sudo apt-get install libmagic1 tesseract-ocr`)
  - **macOS**: `libmagic`, `tesseract` (`brew install libmagic tesseract`)

### Quick Setup

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/book_triage_v0.1.0.git
   cd book_triage_v0.1.0
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/fitydo/book_triage_v0.1.0.git
   ```

## Development Environment Setup

### Using Poetry (Recommended)

```bash
# Install Poetry if you don't have it
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install --with dev

# Activate virtual environment
poetry shell
```

### Using pip

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Platform-Specific Setup

#### Windows
```bash
# Install Windows-specific dependencies
pip install python-magic-bin pywin32 wmi
```

#### Linux (Ubuntu/Debian)
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y libmagic1 tesseract-ocr

# Install Python dependencies
pip install python-magic
```

#### macOS
```bash
# Install system dependencies
brew install libmagic tesseract

# Install Python dependencies
pip install python-magic
```

### Environment Configuration

Create a `.env` file in the project root:

```bash
# Authentication (for testing)
BOOK_USER=testuser
BOOK_PASS=testpass

# OpenAI API (optional, for OCR features)
OPENAI_API_KEY=your_openai_key_here

# Development settings
DEBUG=true
LOG_LEVEL=DEBUG
```

### Verify Installation

```bash
# Run compatibility test
python scripts/test_compatibility.py

# Expected output:
# 🎯 Results: 5/5 tests passed
# 🎉 All tests passed! Book Triage is compatible with this platform.
```

## Coding Standards

We maintain high code quality through automated tooling and consistent standards.

### Code Formatting

**Black** - Code formatter (line length: 88 characters)
```bash
# Format all code
black .

# Check formatting without changes
black --check .
```

**Ruff** - Fast Python linter and formatter
```bash
# Run linting
ruff check .

# Fix auto-fixable issues
ruff check --fix .
```

### Type Checking

**MyPy** - Static type checker
```bash
# Run type checking
mypy book_triage/

# Type checking configuration is in pyproject.toml
```

### Code Style Guidelines

1. **Follow PEP 8** with Black's formatting
2. **Use type hints** for all function signatures
3. **Write docstrings** for all public functions and classes
4. **Use meaningful variable names** and avoid abbreviations
5. **Keep functions small** and focused (max ~50 lines)
6. **Add comments** for complex logic

#### Example Code Style

```python
from typing import List, Optional
from pathlib import Path

def process_book_data(
    csv_path: Path, 
    output_path: Optional[Path] = None
) -> List[str]:
    """Process book data from CSV file.
    
    Args:
        csv_path: Path to input CSV file
        output_path: Optional path for output file
        
    Returns:
        List of processed book IDs
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If CSV format is invalid
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    # Process the data...
    return processed_ids
```

### Pre-commit Hooks (Recommended)

Install pre-commit hooks to automatically check code quality:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

## Testing

We maintain comprehensive test coverage (target: 84%+) across all modules.

### Test Structure

```
tests/
├── __init__.py
├── test_core.py          # Core business logic tests
├── test_api.py           # FastAPI endpoint tests  
├── test_cli.py           # CLI interface tests
├── test_vision.py        # OCR/vision processing tests
└── conftest.py           # Shared test fixtures
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=book_triage --cov-report=html

# Run specific test file
pytest tests/test_core.py -v

# Run specific test
pytest tests/test_core.py::test_book_record_creation -v

# Run with markers
pytest -m "not slow"  # Skip slow tests
```

### Writing Tests

#### Test Guidelines

1. **Use descriptive test names**: `test_book_record_creation_with_valid_data`
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Use fixtures** for common setup
4. **Mock external dependencies** (OpenAI API, file operations)
5. **Test edge cases** and error conditions
6. **Maintain test isolation** - tests should not depend on each other

#### Example Test

```python
import pytest
from unittest.mock import Mock, patch
from book_triage.core import BookRecord

def test_book_record_creation_with_valid_data():
    """Test BookRecord creation with valid input data."""
    # Arrange
    title = "Clean Code"
    url = "https://example.com"
    
    # Act
    record = BookRecord(title=title, url=url)
    
    # Assert
    assert record.title == title
    assert record.url == url
    assert record.id is not None
    assert record.decision == "unknown"

@patch('book_triage.core.openai.OpenAI')
def test_book_triage_with_mocked_openai(mock_openai):
    """Test BookTriage decision making with mocked OpenAI."""
    # Arrange
    mock_client = Mock()
    mock_openai.return_value = mock_client
    
    # Act & Assert
    # ... test implementation
```

### Test Categories

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **API Tests**: Test FastAPI endpoints with TestClient
- **CLI Tests**: Test command-line interface
- **Cross-Platform Tests**: Verify functionality across OS platforms

### Coverage Requirements

- **Minimum coverage**: 84%
- **New code coverage**: 90%+
- **Critical paths**: 100% (authentication, data persistence)

```bash
# Generate coverage report
coverage run -m pytest
coverage report --show-missing
coverage html  # Creates htmlcov/ directory
```

## Pull Request Process

### Before Creating a PR

1. **Sync with upstream**:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** following coding standards

4. **Run quality checks**:
   ```bash
   # Format code
   black .
   ruff check --fix .
   
   # Type checking
   mypy book_triage/
   
   # Run tests
   pytest --cov=book_triage
   
   # Security check
   bandit -r book_triage/
   ```

### Creating the Pull Request

1. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR** on GitHub using our [PR template](.github/PULL_REQUEST_TEMPLATE.md)

3. **Fill out the template** completely:
   - Clear description of changes
   - Link to related issues
   - Test coverage information
   - Cross-platform testing results
   - Documentation updates

### PR Requirements

**Required Checks:**
- [ ] All CI tests pass
- [ ] Code coverage ≥ 84%
- [ ] No security vulnerabilities
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Cross-platform compatibility verified

**Review Process:**
1. **Automated checks** run via GitHub Actions
2. **Code review** by maintainers
3. **Testing** on multiple platforms
4. **Approval** and merge

### PR Guidelines

- **Keep PRs focused** - one feature/fix per PR
- **Write clear commit messages**:
  ```
  feat: add OCR support for book scanning
  
  - Integrate Tesseract OCR for title extraction
  - Add OpenAI Vision API fallback
  - Include error handling for image processing
  
  Closes #123
  ```
- **Update documentation** for user-facing changes
- **Add tests** for new functionality
- **Consider backward compatibility**

## Issue Management

### Creating Issues

Use our issue templates for:
- 🐛 **Bug Reports** - Include reproduction steps, environment details
- ✨ **Feature Requests** - Describe the problem and proposed solution  
- 📚 **Documentation** - Improvements or additions needed
- 🔒 **Security** - Use private disclosure for vulnerabilities

### Issue Labels

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements or additions to docs
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention is needed
- `priority/high` - High priority issue
- `platform/windows` - Windows-specific issue
- `platform/linux` - Linux-specific issue
- `platform/macos` - macOS-specific issue

### Working on Issues

1. **Comment on the issue** to indicate you're working on it
2. **Ask questions** if requirements are unclear
3. **Reference the issue** in your PR (`Closes #123`)

## Branch Strategy

We use **GitHub Flow** with protection on the main branch:

- **`main`** - Production-ready code, protected branch
- **`develop`** - Integration branch for features (optional)
- **`feature/xyz`** - Feature development branches
- **`hotfix/xyz`** - Critical bug fixes
- **`docs/xyz`** - Documentation updates

### Branch Naming

```bash
feature/add-ocr-support
bugfix/fix-csv-parsing-error
docs/update-contributing-guide
hotfix/security-vulnerability-fix
```

## Documentation

### Types of Documentation

1. **Code Documentation** - Docstrings and comments
2. **User Documentation** - README, setup guides
3. **Developer Documentation** - This guide, ADRs
4. **API Documentation** - Auto-generated from FastAPI

### Documentation Standards

- **Use clear, concise language**
- **Include code examples** where helpful
- **Update docs** with code changes
- **Follow markdown standards**

### Architecture Decision Records (ADRs)

For significant architectural changes, create an ADR in `docs/adr/`:

```markdown
# ADR-XXX: Title

## Status
Proposed/Accepted/Deprecated

## Context
What is the issue that we're seeing that is motivating this decision?

## Decision
What is the change that we're proposing and/or doing?

## Consequences
What becomes easier or more difficult to do because of this change?
```

## Release Process

### Versioning

We follow **Semantic Versioning** (SemVer):
- **MAJOR** version for incompatible API changes
- **MINOR** version for backward-compatible functionality additions  
- **PATCH** version for backward-compatible bug fixes

### Release Checklist

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with release notes
3. **Create release PR** to main branch
4. **Tag release** after merge
5. **GitHub Actions** automatically:
   - Builds cross-platform distributions
   - Runs comprehensive tests
   - Creates GitHub release
   - Uploads artifacts

## Getting Help

### Communication Channels

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - General questions and ideas
- **Pull Request Reviews** - Code-specific discussions

### Maintainer Response Times

- **Bug reports**: 1-3 business days
- **Feature requests**: 1-2 weeks  
- **Pull request reviews**: 2-5 business days
- **Security issues**: 24-48 hours

### Development Tips

1. **Start small** - Look for `good first issue` labels
2. **Ask questions** - Don't hesitate to ask for clarification
3. **Test thoroughly** - Verify changes work across platforms
4. **Follow patterns** - Look at existing code for consistency
5. **Be patient** - Quality takes time, and we appreciate it!

## Recognition

Contributors are recognized in:
- **CONTRIBUTORS.md** file (coming soon)
- **GitHub releases** changelog
- **Annual contributor highlights**

Thank you for contributing to Book Triage! 🎉

---

## Quick Reference

### Essential Commands

```bash
# Setup
git clone https://github.com/YOUR_USERNAME/book_triage_v0.1.0.git
cd book_triage_v0.1.0
pip install -e ".[dev]"

# Quality checks
black . && ruff check --fix . && mypy book_triage/

# Testing
pytest --cov=book_triage --cov-report=html

# Before PR
git fetch upstream && git rebase upstream/main
```

### File Locations

- **Main code**: `book_triage/`
- **Tests**: `tests/`
- **Documentation**: `docs/`
- **Scripts**: `scripts/`
- **Config**: `pyproject.toml`
- **Dependencies**: `requirements.txt`

Happy coding! 🚀