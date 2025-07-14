# Book Triage v0.1.0 - Cross-Platform Release 🚀

## 🎯 What's New

This release brings Book Triage to **Windows 11**, **Linux**, and **macOS** with full cross-platform compatibility and verified functionality.

### ✨ New Features
- **Cross-platform compatibility** verified on Windows 11, Linux, and macOS
- **Platform-specific installers** for easy setup
- **Automated dependency management** for each platform
- **Comprehensive compatibility testing** suite
- **Security hardening** with authentication and rate limiting
- **High-performance API** (150-300+ RPS)

### 🔒 Security Enhancements
- HTTP Basic Authentication
- Rate limiting (60 req/min default)
- File upload validation (10MB limit)
- Security headers (CSP, HSTS, etc.)
- Input sanitization and SQL injection prevention

### 📊 Performance
- **Response Time**: <50ms average for API endpoints
- **Throughput**: 150-300+ requests per second
- **Reliability**: 97%+ success rate under chaos testing
- **Memory Usage**: 150-300MB typical

## 📦 Downloads

Choose the appropriate package for your platform:

### 🪟 Windows 11
**`book-triage-v0.1.0-windows.zip`** (0.1MB)
- **Requirements**: Python 3.12+, Windows 10/11
- **Installation**: Extract and run `install.bat`
- **Startup**: Double-click `start.bat`
- **Dependencies**: Auto-installs `python-magic-bin`, `colorama`

### 🐧 Linux
**`book-triage-v0.1.0-linux.tar.gz`** (0.1MB)
- **Requirements**: Python 3.12+, Ubuntu 20.04+/CentOS 8+
- **Installation**: `tar -xzf book-triage-v0.1.0-linux.tar.gz && ./install.sh`
- **Startup**: `./start.sh`
- **Dependencies**: Auto-installs `libmagic1`, `tesseract-ocr`

### 🍎 macOS
**`book-triage-v0.1.0-macos.zip`** (0.1MB)  
- **Requirements**: Python 3.12+, macOS 10.15+ (Intel & Apple Silicon)
- **Installation**: Extract and run `./install.sh`
- **Startup**: `./start.sh`
- **Dependencies**: Uses Homebrew for `libmagic`, `tesseract`

## 🚀 Quick Start

### 1. Download & Extract
Download the appropriate package for your platform and extract it.

### 2. Install Dependencies
```bash
# Windows: Double-click install.bat
# Linux/macOS: ./install.sh
```

### 3. Start the Application
```bash
# Windows: Double-click start.bat
# Linux/macOS: ./start.sh
```

### 4. Open Your Browser
Navigate to `http://localhost:8000` to access the web interface.

## 🔧 Manual Installation

If automated installers don't work:

```bash
# 1. Install Python 3.12+
# 2. Extract the package
# 3. Install dependencies
pip install -e .

# Platform-specific:
# Windows: pip install python-magic-bin colorama
# Linux: sudo apt-get install libmagic1 tesseract-ocr && pip install python-magic  
# macOS: brew install libmagic tesseract && pip install python-magic

# 4. Setup environment
cp .env.example .env

# 5. Start the application
python -m uvicorn book_triage.api:app --reload
```

## 🧪 Verification

Test your installation:

```bash
# Run compatibility test
python scripts/test_compatibility.py

# Expected output:
# 🎯 Results: 5/5 tests passed
# 🎉 All tests passed! Book Triage is compatible with this platform.
```

## 📋 System Requirements

### Minimum
- **Python**: 3.12 or higher
- **RAM**: 512MB available
- **Storage**: 500MB free space
- **Network**: Internet connection (for AI features)

### Recommended  
- **Python**: 3.12+ with pip
- **RAM**: 2GB available
- **Storage**: 1GB free space
- **OCR**: Tesseract for image processing

## 🎯 Platform Compatibility

| Feature | Windows 11 | Linux | macOS |
|---------|------------|-------|-------|
| Web Interface | ✅ | ✅ | ✅ |
| CLI Tools | ✅ | ✅ | ✅ |
| File Processing | ✅ | ✅ | ✅ |
| OCR Integration | ✅ | ✅ | ✅ |
| Security Features | ✅ | ✅ | ✅ |

## 🔐 Default Configuration

- **Web Interface**: `http://localhost:8000`
- **Authentication**: `admin` / `password` (⚠️ change immediately!)
- **Rate Limit**: 60 requests/minute
- **File Upload**: 10MB maximum
- **CSV Location**: `examples/sample_books.csv`

## 📚 Documentation

- **[Setup Guide](docs/SETUP_INSTRUCTIONS.md)**: Detailed installation instructions
- **[Distribution Guide](docs/DISTRIBUTIONS.md)**: Platform-specific notes
- **[Security Analysis](docs/SECURITY_ANALYSIS.md)**: Security features and best practices
- **[Performance Report](docs/PERFORMANCE_SUMMARY.md)**: Load testing results
- **[API Documentation](README.md#usage-examples)**: API usage and examples

## 🛠️ Development

To contribute or modify Book Triage:

```bash
# Clone the repository
git clone https://github.com/fitydo/book_triage_v1.0.0.git
cd book-triage

# Install development dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest tests/ -v

# Run security tests
python scripts/security_audit.py

# Run performance tests
python scripts/comprehensive_rps_test.py
```

## 🐛 Known Issues

### Windows 11
- Antivirus software may flag batch files (safe to allow)
- Some corporate environments may block PowerShell execution

### Linux
- Requires sudo access for system dependencies
- Some distributions may need additional packages

### macOS
- Gatekeeper may require allowing unsigned applications
- Homebrew required for optimal experience

## 🆘 Troubleshooting

### Common Issues

**Python not found**
- Install Python 3.12+ from [python.org](https://python.org/downloads/)
- Ensure Python is in your system PATH

**Permission denied**
- Windows: Run as Administrator
- Linux/macOS: Use `sudo` for system dependencies

**Dependencies fail to install**
- Update pip: `python -m pip install --upgrade pip`
- Install build tools (Windows: Visual Studio Build Tools)

**Import errors**
- Check Python version: `python --version`
- Verify package installation: `pip list | grep book-triage`

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/fitydo/book_triage_v1.0.0/issues)
- **Discussions**: [GitHub Discussions](https://github.com/fitydo/book_triage_v1.0.0/discussions)  
- **Documentation**: Complete guides in repository

## 🙏 Acknowledgments

- **FastAPI**: Modern web framework
- **Typer**: Excellent CLI framework
- **Pandas**: Data processing powerhouse
- **Tesseract**: OCR functionality
- **OpenAI**: Vision API integration

## 📈 What's Next

- **v0.2.0**: Enhanced OCR processing
- **Mobile support**: iOS/Android compatibility
- **Docker containers**: Containerized deployment
- **Cloud deployment**: AWS/Azure/GCP guides
- **API improvements**: GraphQL support

---

**⭐ Star this repository if Book Triage helps you organize your book collection!**

**📧 Questions?** Open an issue or start a discussion.

**🔗 Share** this release with fellow book lovers and developers! 