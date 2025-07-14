# Book Triage

![CI](https://github.com/fitydo/book_triage_v0.1.0/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/fitydo/book_triage_v0.1.0/branch/main/graph/badge.svg)](https://codecov.io/gh/fitydo/book_triage_v0.1.0)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Windows](https://img.shields.io/badge/Windows-11-blue)](https://github.com/fitydo/book_triage_v0.1.0/releases)
[![Linux](https://img.shields.io/badge/Linux-Ubuntu%2020.04+-orange)](https://github.com/fitydo/book_triage_v0.1.0/releases)
[![macOS](https://img.shields.io/badge/macOS-10.15+-lightgrey)](https://github.com/fitydo/book_triage_v0.1.0/releases)

A comprehensive Python tool for triaging books based on frequency, rarity, annotation needs, and other factors to help you decide whether to sell, digitize, or keep your books. Features a FastAPI web interface, CLI tools, and OCR capabilities for efficient book collection management.

**✅ Verified compatible with Windows 11, Linux, and macOS**

## 📦 Installation

### Method 1: Direct from Source (Recommended)

```bash
# Clone the repository
git clone https://github.com/fitydo/book_triage_v0.1.0.git
cd book_triage_v0.1.0

# Install dependencies
pip install -e .

# Verify installation
python -m book_triage --help
```

### Method 2: Using pip (when available)

```bash
# Install from PyPI (coming soon)
pip install book-triage

# Or install from GitHub directly
pip install git+https://github.com/fitydo/book_triage_v0.1.0.git
```

### Method 3: Platform-Specific Packages

**📦 Pre-built packages available in the `distributions/` folder:**
- 🪟 **Windows**: `distributions/windows/` - See [Windows Installation Guide](INSTALL_WINDOWS.md)
- 🐧 **Linux**: `distributions/linux/` - Shell scripts and installation
- 🍎 **macOS**: `distributions/macos/` - Native macOS support

### 🪟 Windows Users - Important!

If you're on Windows and experiencing issues with git clone (Zone.Identifier errors), please see the detailed [Windows Installation Guide](INSTALL_WINDOWS.md) for step-by-step instructions and troubleshooting.

## ✨ Features

- **📊 Multi-criteria Decision Framework**: FRAVSP scoring system (Frequency, Rarity, Annotation, Value, Space, Personal)
- **🌐 Web Interface**: Modern FastAPI-based web UI with file uploads and real-time processing
- **🖥️ Command Line Interface**: Full CLI support with Typer for automation and scripting
- **🔍 OCR Integration**: Tesseract and OpenAI Vision API support for book scanning
- **🔒 Security Hardened**: HTTP Basic Auth, rate limiting, file validation, security headers
- **📈 High Performance**: 150-300+ RPS capacity with comprehensive load testing
- **🧪 Chaos Engineering**: Built-in resilience testing and failure simulation
- **📝 CSV Data Management**: Pandas-based data persistence and manipulation
- **🌍 Cross-Platform**: Native support for Windows 11, Linux, and macOS

## 🚀 Quick Start

### Step 1: Install Book Triage

Choose your preferred installation method from above. For beginners, we recommend Method 1 (Direct from Source).

### Step 2: Set up Environment (Optional)

Create a `.env` file in the project directory:

```bash
BOOK_USER=your_username
BOOK_PASS=your_password
OPENAI_API_KEY=your_openai_key  # Optional, for OCR features
```

### Step 3: Create Sample Data

```bash
# Create a sample CSV file
python -m book_triage create-csv sample_books.csv --sample
```

### Step 4: Start Using Book Triage

**Web Interface:**
```bash
# Start the web server
python -m book_triage web sample_books.csv
# Open http://localhost:8000 in your browser
```

**Command Line:**
```bash
# Scan books from command line
python -m book_triage scan sample_books.csv
```

## 🧪 Verify Installation

Test your setup works correctly:

```bash
# Run installation test
python test_installation.py

# Expected output:
# 🎯 Results: 5/5 tests passed
# 🎉 All tests passed! Book Triage is ready to use.
```

If any tests fail, check the troubleshooting section in the output.

## 📁 Project Structure

```
book-triage/
├── 📂 book_triage/          # Core application package
│   ├── api.py              # FastAPI web interface
│   ├── cli.py              # Command line interface
│   ├── core.py             # Business logic and scoring
│   ├── vision.py           # OCR and image processing
│   └── security.py         # Authentication and validation
├── 📂 tests/               # Comprehensive test suite (85%+ coverage)
├── 📂 docs/                # Documentation and reports
├── 📂 scripts/             # Utility scripts and tools
├── 📂 examples/            # Sample data and usage examples
├── 📂 distributions/       # Platform-specific packages
├── 📂 .github/workflows/   # CI/CD pipeline
├── 📄 README.md            # This file
├── 📄 LICENSE              # MIT License
└── 📄 pyproject.toml       # Project configuration
```

## 🔧 Configuration

Create a `.env` file with the following variables:

```bash
BOOK_USER=your_username
BOOK_PASS=your_password
OPENAI_API_KEY=your_openai_key  # Optional, for OCR features
```

## 🔧 Troubleshooting

### Common Installation Issues

**Problem: ModuleNotFoundError**
```bash
# Solution: Install dependencies
pip install -e .
```

**Problem: Permission denied**
```bash
# Solution: Use user installation
pip install --user -e .
```

**Problem: Web server won't start**
```bash
# Solution: Try a different port
python -m book_triage web books.csv --port 8001
```

**Problem: OCR not working**
```bash
# Solution: Install tesseract
# Ubuntu/Debian: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
```

**Problem: Windows git clone fails with Zone.Identifier errors**
```powershell
# Solution: Use git with NTFS protection disabled
git clone -c core.protectNTFS=false https://github.com/fitydo/book_triage_v0.1.0.git

# Or download as ZIP file from GitHub instead
```

**Problem: "Neither 'setup.py' nor 'pyproject.toml' found" on Windows**
```powershell
# Solution: Git checkout failed, restore working tree
git restore --source=HEAD :/

# Or re-clone with the fix above
```

### Getting Help

- Check the [Issues](https://github.com/fitydo/book_triage_v0.1.0/issues) page
- Run `python test_installation.py` to diagnose problems
- Check the logs in the terminal output

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

## 🛠️ Development

### Development Installation

```bash
git clone https://github.com/fitydo/book_triage_v0.1.0.git
cd book-triage
pip install -e .
```

### Cross-Platform Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Platform-specific setup
# Windows: pip install python-magic-bin
# Linux: sudo apt-get install libmagic1 tesseract-ocr
# macOS: brew install libmagic tesseract

# Run full test suite
python scripts/run_tests.py

# Test specific platforms
python scripts/test_compatibility.py

# Create distributions
python scripts/create_distributions_simple.py
```

### Quality Assurance

```bash
# Unit tests with coverage
python -m pytest tests/ --cov=book_triage --cov-report=html

# Performance testing
python scripts/comprehensive_rps_test.py

# Security testing
python scripts/security_audit.py

# Chaos engineering
python scripts/chaos_demo.py
```

## 🤝 Contributing & Support

- **🐛 Bug Reports**: [GitHub Issues](https://github.com/fitydo/book_triage_v0.1.0/issues)
- **💬 Questions**: [GitHub Discussions](https://github.com/fitydo/book_triage_v0.1.0/discussions)
- **📖 Documentation**: [Project Wiki](https://github.com/fitydo/book_triage_v0.1.0/wiki)

## 📋 Documentation

- **[Distributions Guide](docs/DISTRIBUTIONS.md)** - Platform-specific installation and notes
- **[Setup Instructions](docs/SETUP_INSTRUCTIONS.md)** - Detailed installation guide
- **[Security Analysis](docs/SECURITY_ANALYSIS.md)** - Security features and hardening
- **[Performance Testing](docs/PERFORMANCE_SUMMARY.md)** - Load testing and benchmarks
- **[Testing Guide](docs/TESTING.md)** - Running tests and quality assurance
- **[DAST Security Report](docs/DAST_SUMMARY.md)** - Security vulnerability testing

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

### Platform-Specific Help

**Windows Issues:**
- Install Python from [python.org](https://python.org/downloads/)
- Run as Administrator if permission errors
- Allow batch files in antivirus software

**Linux Issues:**
- Update packages: `sudo apt-get update`
- Install build tools: `sudo apt-get install build-essential`
- Check Python: `python3 --version`

**macOS Issues:**
- Install Xcode tools: `xcode-select --install`
- Use Homebrew: `brew install python@3.12`
- Allow unsigned apps in System Preferences

### Getting Help

- **📧 Security Issues**: security@booktriage.com

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) for the web interface
- [Typer](https://typer.tiangolo.com/) for the CLI
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for image processing
- [Pandas](https://pandas.pydata.org/) for data management
- Tested on GitHub Actions across multiple platforms

## 🌍 Platform Support

| Platform | Status | Python | Package Manager | Notes |
|----------|--------|--------|------------------|-------|
| **Windows 11** | ✅ Verified | 3.12+ | pip | Auto-installer included |
| **Windows 10** | ✅ Compatible | 3.12+ | pip | Use Windows 11 package |
| **Ubuntu 20.04+** | ✅ Verified | 3.12+ | apt | System deps included |
| **CentOS 8+** | ✅ Compatible | 3.12+ | yum/dnf | Manual system deps |
| **Debian 11+** | ✅ Compatible | 3.12+ | apt | System deps included |
| **macOS 10.15+** | ✅ Verified | 3.12+ | brew | Intel & Apple Silicon |
| **Arch Linux** | ⚠️ Compatible | 3.12+ | pacman | Manual testing needed |
| **Docker** | 🔄 Coming Soon | 3.12+ | - | v0.2.0 planned |

### System Requirements

**Minimum:**
- Python 3.12+, 512MB RAM, 500MB storage

**Recommended:**
- Python 3.12+, 2GB RAM, 1GB storage, Tesseract OCR

## 🎯 Roadmap

### v0.2.0 (Next Release)
- 🐳 **Docker containers** for easy deployment
- 📱 **Mobile-responsive UI** improvements
- 🔍 **Enhanced OCR** with multiple engines
- ☁️ **Cloud deployment** guides (AWS, Azure, GCP)

### v0.3.0 (Future)
- 📱 **Mobile apps** (iOS/Android)
- 🌐 **Multi-language** support
- 🔗 **API integrations** (Goodreads, Amazon)
- 📊 **Analytics dashboard** with insights 