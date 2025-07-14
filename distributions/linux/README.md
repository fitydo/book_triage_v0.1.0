# Book Triage

![CI](https://github.com/fitydo/book_triage_v1.0.0/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/fitydo/book_triage_v1.0.0/branch/main/graph/badge.svg)](https://codecov.io/gh/fitydo/book_triage_v1.0.0)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

A comprehensive Python tool for triaging books based on frequency, rarity, annotation needs, and other factors to help you decide whether to sell, digitize, or keep your books. Features a FastAPI web interface, CLI tools, and OCR capabilities for efficient book collection management.

## ✨ Features

- **📊 Multi-criteria Decision Framework**: FRAVSP scoring system (Frequency, Rarity, Annotation, Value, Space, Personal)
- **🌐 Web Interface**: Modern FastAPI-based web UI with file uploads and real-time processing
- **🖥️ Command Line Interface**: Full CLI support with Typer for automation and scripting
- **🔍 OCR Integration**: Tesseract and OpenAI Vision API support for book scanning
- **🔒 Security Hardened**: HTTP Basic Auth, rate limiting, file validation, security headers
- **📈 High Performance**: 150-300+ RPS capacity with comprehensive load testing
- **🧪 Chaos Engineering**: Built-in resilience testing and failure simulation
- **📝 CSV Data Management**: Pandas-based data persistence and manipulation

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/fitydo/book_triage_v1.0.0.git
cd book_triage_v1.0.0

# Install dependencies
pip install -e .

# Set up environment variables
cp book_triage/env_example.txt .env
# Edit .env with your configuration
```

### Basic Usage

```bash
# Start the web interface
python -m uvicorn book_triage.api:app --reload

# Use the CLI
python -m book_triage.cli add-book "Title" "https://example.com" --decision keep

# Run with sample data
python -m book_triage.cli process examples/sample_books.csv
```

## 📁 Project Structure

```
book-triage/
├── book_triage/           # Core application package
│   ├── api.py            # FastAPI web interface
│   ├── cli.py            # Command line interface
│   ├── core.py           # Business logic and scoring
│   ├── vision.py         # OCR and image processing
│   └── security.py       # Authentication and validation
├── tests/                # Comprehensive test suite
├── docs/                 # Documentation and reports
├── scripts/              # Utility scripts and tools
├── examples/             # Sample data and usage examples
├── .github/workflows/    # CI/CD pipeline
└── pyproject.toml        # Project configuration
```

## 🔧 Configuration

Create a `.env` file with the following variables:

```bash
BOOK_USER=your_username
BOOK_PASS=your_password
OPENAI_API_KEY=your_openai_key  # Optional, for OCR features
```

## 📖 Usage Examples

### Web Interface
```bash
# Start the server
python -m uvicorn book_triage.api:app --host 0.0.0.0 --port 8000

# Access at http://localhost:8000
# Upload CSV files or scan book covers
```

### Command Line
```bash
# Add a single book
python -m book_triage.cli add-book "Programming Pearls" "https://example.com" --F 5 --R 3 --A 4

# Process a CSV file
python -m book_triage.cli process examples/sample_books.csv --output results.csv

# Scan a book cover image
python -m book_triage.cli scan-image book_cover.jpg --provider openai
```

### Python API
```python
from book_triage.core import BookTriageManager
from pathlib import Path

# Initialize manager
manager = BookTriageManager(Path("books.csv"))

# Add and score a book
book_id = manager.add_book("Clean Code", "https://example.com")
manager.update_scores(book_id, F=5, R=2, A=4, V=3, S=2, P=5)
decision = manager.make_decision(book_id)
```

## 🧪 Testing & Quality Assurance

```bash
# Run unit tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=book_triage --cov-report=html

# Performance testing
python scripts/comprehensive_rps_test.py

# Security testing
python scripts/security_audit.py

# Chaos engineering
python scripts/chaos_demo.py
```

## 🔒 Security Features

- **HTTP Basic Authentication** with configurable credentials
- **Rate Limiting** (60 req/min default, 30 req/min for data endpoints)
- **File Upload Validation** with magic number verification and size limits
- **Security Headers** (CSP, X-Frame-Options, HSTS, etc.)
- **Input Sanitization** and SQL injection prevention
- **HTTPS Enforcement** for production deployments

## 📊 Performance Metrics

- **Throughput**: 150-300+ requests per second
- **Response Time**: <50ms average for API endpoints
- **Reliability**: 97%+ success rate under chaos testing
- **Coverage**: 85%+ code coverage with comprehensive test suite

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run pre-commit hooks
pre-commit install

# Run the full test suite
python scripts/run_tests.py
```

## 📋 Documentation

- [Setup Instructions](docs/SETUP_INSTRUCTIONS.md)
- [Security Analysis](docs/SECURITY_ANALYSIS.md)
- [Performance Testing](docs/PERFORMANCE_SUMMARY.md)
- [Testing Guide](docs/TESTING.md)
- [DAST Security Report](docs/DAST_SUMMARY.md)

## 🏗️ Architecture

The Book Triage system uses a modular architecture:

- **Core Engine** (`core.py`): FRAVSP scoring algorithm and decision logic
- **Web Interface** (`api.py`): FastAPI-based REST API with modern UI
- **CLI Interface** (`cli.py`): Typer-based command line tools
- **Vision Processing** (`vision.py`): OCR integration with Tesseract and OpenAI
- **Security Layer** (`security.py`): Authentication, validation, and rate limiting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/fitydo/book_triage_v1.0.0/issues)
- **Discussions**: [GitHub Discussions](https://github.com/fitydo/book_triage_v1.0.0/discussions)
- **Documentation**: [Project Wiki](https://github.com/fitydo/book_triage_v1.0.0/wiki)

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) for the web interface
- [Typer](https://typer.tiangolo.com/) for the CLI
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for image processing
- [Pandas](https://pandas.pydata.org/) for data management 