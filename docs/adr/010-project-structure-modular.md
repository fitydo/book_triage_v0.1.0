# ADR-010: Modular Project Structure

## Status
Accepted

## Context
Book Triage requires a clean, maintainable project structure that supports multiple interfaces (CLI, web API), cross-platform distribution, comprehensive testing, and future extensibility. The project structure must facilitate development, testing, deployment, and community contributions.

**Requirements:**
- Separation of concerns (core logic, interfaces, utilities)
- Support for multiple entry points (CLI, web)
- Clear testing organization
- Cross-platform compatibility
- Documentation structure
- Distribution packaging
- CI/CD integration

## Decision
We will implement a **modular project structure** with:

1. **Core Package** - `book_triage/` with business logic modules
2. **Interface Separation** - CLI and API as separate modules
3. **Utility Organization** - Scripts, tests, docs in dedicated directories
4. **Distribution Support** - Cross-platform packages in `distributions/`
5. **Professional Layout** - Standard Python project conventions

## Consequences

### Positive
- **Maintainability**: Clear separation of concerns
- **Testability**: Organized test structure mirrors code
- **Extensibility**: Easy to add new interfaces or features
- **Distribution**: Clean packaging for releases
- **Community**: Standard structure for contributors
- **Documentation**: Organized docs and examples

### Negative
- **Initial Complexity**: More directories to manage
- **Import Complexity**: Module imports require careful design
- **Synchronization**: Multiple distribution copies to maintain

## Implementation

### Root Project Structure
```
book-triage/
├── book_triage/              # Core Python package
│   ├── __init__.py          # Package initialization
│   ├── core.py              # Business logic (BookTriage, BookRecord)
│   ├── api.py               # FastAPI web interface
│   ├── cli.py               # Typer CLI interface
│   ├── vision.py            # OCR and image processing
│   ├── security.py          # Authentication and security
│   └── env_example.txt      # Environment template
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_core.py         # Core business logic tests
│   ├── test_api.py          # API endpoint tests
│   ├── test_cli.py          # CLI command tests
│   ├── test_vision.py       # Vision processing tests
│   └── test_vision_fixed.py # Additional vision tests
├── scripts/                 # Utility scripts
│   ├── README.md            # Scripts documentation
│   ├── create_distributions_simple.py
│   ├── test_compatibility.py
│   ├── chaos_demo.py
│   └── ...                  # Other utility scripts
├── docs/                    # Documentation
│   ├── adr/                 # Architecture Decision Records
│   ├── SETUP_INSTRUCTIONS.md
│   ├── SECURITY_ANALYSIS.md
│   └── ...                  # Other documentation
├── examples/                # Sample data and usage
│   ├── README.md            # Examples documentation
│   └── sample_books.csv     # Sample data file
├── distributions/           # Cross-platform packages
│   ├── book-triage-0.1.0-windows.zip
│   ├── book-triage-0.1.0-linux.tar.gz
│   ├── book-triage-0.1.0-macos.zip
│   ├── windows/             # Windows package contents
│   ├── linux/               # Linux package contents
│   └── macos/               # macOS package contents
├── .github/                 # GitHub configuration
│   ├── workflows/           # CI/CD pipelines
│   │   └── ci.yml
│   └── RELEASE_TEMPLATE.md  # Release template
├── pyproject.toml           # Project configuration
├── requirements.txt         # Dependencies
├── README.md                # Main documentation
├── LICENSE                  # MIT License
├── .gitignore              # Git ignore rules
└── .env.example            # Environment template
```

### Core Package Design (`book_triage/`)

#### Module Responsibilities
- **`core.py`**: Business logic, data structures, FRAVSP calculations
- **`api.py`**: FastAPI web interface, HTTP endpoints
- **`cli.py`**: Typer CLI interface, command definitions
- **`vision.py`**: OCR processing, image handling
- **`security.py`**: Authentication, authorization, security utilities

#### Clean Imports
```python
# book_triage/__init__.py
"""Book Triage - CSV-based book collection management"""

__version__ = "0.1.0"

from .core import BookTriage, BookRecord, Decision
from .api import app, initialize_app
from .cli import main as cli_main

__all__ = ["BookTriage", "BookRecord", "Decision", "app", "initialize_app", "cli_main"]
```

### Testing Organization (`tests/`)

#### Test Structure Mirrors Code
```python
tests/
├── test_core.py              # Tests for book_triage.core
├── test_api.py               # Tests for book_triage.api
├── test_cli.py               # Tests for book_triage.cli
├── test_vision.py            # Tests for book_triage.vision
└── test_vision_fixed.py      # Additional vision tests
```

#### Comprehensive Test Coverage
- **94 total tests** across all modules
- **Unit tests** for individual functions
- **Integration tests** for API endpoints
- **CLI tests** with command simulation
- **Security tests** for authentication

### Documentation Structure (`docs/`)

#### Organized Documentation
```
docs/
├── adr/                      # Architecture Decision Records
│   ├── README.md            # ADR index
│   ├── 001-data-storage-csv.md
│   ├── 002-web-framework-fastapi.md
│   └── ...                  # All 10 ADRs
├── SETUP_INSTRUCTIONS.md     # Installation guide
├── SECURITY_ANALYSIS.md      # Security documentation
├── DISTRIBUTIONS.md          # Platform guides
└── ...                      # Other documentation
```

### Script Organization (`scripts/`)

#### Utility Scripts
```
scripts/
├── README.md                        # Scripts documentation
├── create_distributions_simple.py   # Build distributions
├── test_compatibility.py            # Platform testing
├── chaos_demo.py                    # Security testing
├── comprehensive_rps_test.py        # Performance testing
└── ...                              # Other utilities
```

## Module Design Principles

### Separation of Concerns
```python
# Clear responsibility boundaries
book_triage/
├── core.py      # Business logic only
├── api.py       # HTTP interface only  
├── cli.py       # Command-line interface only
├── vision.py    # Image processing only
└── security.py  # Security features only
```

### Dependency Management
```python
# Core module has minimal dependencies
# Interface modules import from core
# No circular dependencies

# Good: API imports from core
from book_triage.core import BookTriage

# Good: CLI imports from core
from book_triage.core import BookTriage

# Avoid: Core importing from interfaces
```

### Entry Points
```python
# pyproject.toml
[project.scripts]
book-triage = "book_triage.cli:main"

[project.entry-points."fastapi.apps"]
book-triage-api = "book_triage.api:app"
```

## Cross-Platform Distribution

### Distribution Package Structure
```
distributions/
├── windows/                 # Windows-specific package
│   ├── book_triage/        # Core package copy
│   ├── install.bat         # Windows installer
│   ├── start.bat           # Windows launcher
│   └── README_WINDOWS.txt  # Windows instructions
├── linux/                  # Linux-specific package
│   ├── book_triage/        # Core package copy
│   ├── install.sh          # Linux installer
│   ├── start.sh            # Linux launcher
│   └── README_LINUX.txt    # Linux instructions
└── macos/                  # macOS-specific package
    ├── book_triage/        # Core package copy
    ├── install.sh          # macOS installer
    ├── start.sh            # macOS launcher
    └── README_MACOS.txt    # macOS instructions
```

## Configuration Management

### Environment Configuration
```python
# Centralized configuration
book_triage/env_example.txt    # Template
.env.example                   # Root template
```

### Project Configuration
```toml
# pyproject.toml - Single source of truth
[project]
name = "book-triage"
version = "0.1.0"
description = "CSV-based book collection management"

[project.optional-dependencies]
test = ["pytest>=7.0.0", "pytest-asyncio>=0.20.0"]
security = ["bandit>=1.7.0", "safety>=2.0.0"]
```

## Related Decisions
All ADRs support this modular structure:
- [ADR-001: CSV Storage](001-data-storage-csv.md) - Core data layer
- [ADR-002: FastAPI](002-web-framework-fastapi.md) - API module
- [ADR-003: Authentication](003-authentication-http-basic.md) - Security module
- [ADR-005: Testing](005-testing-strategy-comprehensive.md) - Test organization
- [ADR-006: Distribution](006-cross-platform-distribution.md) - Package structure
- [ADR-007: CI/CD](007-ci-cd-github-actions.md) - Build automation 