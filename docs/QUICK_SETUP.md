# Quick Setup Guide

Get Book Triage running in 5 minutes with this streamlined setup guide.

## 🚀 Local Development Setup

### 1. Clone and Install
```bash
git clone https://github.com/fitydo/book_triage_v1.0.0.git
cd book-triage
pip install -e .
```

### 2. Set Environment Variables
```bash
export BOOK_USER="admin"
export BOOK_PASS="your-password"
export OPENAI_API_KEY="your-openai-key"  # Optional, for AI features
```

### 3. Start the Application
```bash
# Web interface
python -m book_triage.api

# CLI interface  
python -m book_triage.cli --help
```

Visit `http://localhost:8000` for the web interface.

## 📦 Using Pre-built Packages

### Windows
1. Download `book-triage-0.1.0-windows.zip`
2. Extract and run `start.bat`

### Linux/macOS
1. Download the appropriate package
2. Extract and run `./start.sh`

## 🔧 GitHub Repository Setup

If you're setting up this project in your own GitHub repository:

### 1. Required Secrets
Set up these GitHub repository secrets for CI/CD:

- **`CODECOV_TOKEN`** (Required): For code coverage reporting
- **`SLACK_WEBHOOK`** (Optional): For CI failure notifications

📖 **Detailed Instructions**: See [GitHub Secrets Configuration](GITHUB_SECRETS.md)

### 2. Update URLs
Replace `<org>` placeholders in these files with your GitHub organization:
- `.github/ISSUE_TEMPLATE/config.yml`
- `README.md`
- Documentation links

### 3. Codecov Setup
1. Sign up at [codecov.io](https://codecov.io)
2. Connect your repository
3. Add the `CODECOV_TOKEN` secret to GitHub
4. Push a commit to trigger CI and verify coverage reporting

## 🧪 Testing Setup

### Run Tests Locally
```bash
# Install test dependencies
pip install pytest pytest-cov coverage

# Run tests with coverage
coverage run -m pytest tests/ -v
coverage report --show-missing
coverage html  # Generate HTML report
```

### Sample Data
The project includes sample data in `examples/sample_books.csv` for testing.

## 🐳 Docker Setup (Optional)

```bash
# Build image
docker build -t book-triage .

# Run container
docker run -p 8000:8000 \
  -e BOOK_USER=admin \
  -e BOOK_PASS=password \
  book-triage
```

## 🔍 Verification Checklist

- [ ] Application starts without errors
- [ ] Web interface accessible at localhost:8000
- [ ] CLI commands work (`--help`, `--version`)
- [ ] Tests pass locally
- [ ] GitHub CI pipeline passes (if using GitHub)
- [ ] Coverage reports appear on Codecov (if configured)

## 📚 Next Steps

- **Configuration**: See [Setup Instructions](SETUP_INSTRUCTIONS.md) for detailed configuration
- **Development**: Check [Distribution Guide](DISTRIBUTION_GUIDE.md) for packaging
- **Architecture**: Review [UML Documentation](uml/README.md) for system design
- **Contributing**: Read issue templates and PR guidelines

## 🆘 Troubleshooting

### Common Issues

**Import Errors**: Ensure you installed with `pip install -e .`

**Port 8000 Busy**: Change port with `--port 8001` or kill existing processes

**Missing Dependencies**: Install system dependencies:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr libmagic1

# macOS
brew install tesseract libmagic

# Windows
# Tesseract: Download from GitHub releases
# libmagic: Included in python-magic-bin
```

**Environment Variables**: Create a `.env` file:
```
BOOK_USER=admin
BOOK_PASS=your-password
OPENAI_API_KEY=your-key
```

### Getting Help

- 🐛 **Bugs**: Use bug report template
- ❓ **Questions**: Use question template  
- 💡 **Features**: Use feature request template
- 💬 **Discussions**: GitHub Discussions tab

## 🏃‍♂️ Quick Commands Reference

```bash
# Development
python -m book_triage.api                    # Start web server
python -m book_triage.cli add "Book Title"   # Add book via CLI
python -m book_triage.cli list               # List all books

# Testing
pytest tests/                                # Run tests
coverage run -m pytest && coverage report    # Test with coverage

# Building
python -m build                              # Build distribution packages
```

---

**Ready to contribute?** Check out our [issue templates](.github/ISSUE_TEMPLATE/) and [pull request template](.github/PULL_REQUEST_TEMPLATE.md)! 