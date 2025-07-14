# Book Triage App - Distribution Guide

## 📦 How to Share This App

### Option 1: Complete Folder Distribution

**What to give them:**
```
📁 book_triage_app/
├── 📁 book_triage/          # Main app code
├── 📁 tests/               # Tests (optional)
├── 📄 pyproject.toml       # Dependencies
├── 📄 README.md            # Instructions
├── 📄 sample_books.csv     # Sample data
├── 📄 .env.example         # Environment template
├── 🚀 start_book_triage.bat # Windows launcher
├── 🚀 start_simple.bat     # Backup launcher
├── 🚀 start_book_triage.ps1 # PowerShell launcher
└── 📄 SETUP_INSTRUCTIONS.md # Setup guide
```

**Instructions for recipients:**
1. Download and extract the folder
2. Install Python 3.12+ from python.org
3. Copy `.env.example` to `.env` and add OpenAI API key
4. Double-click `start_book_triage.bat`
5. Open browser to `http://localhost:8000`

### Option 2: GitHub Repository

**Steps:**
1. Create GitHub repository
2. Push all code
3. Share the repository URL
4. Recipients clone and follow README

### Option 3: Executable Distribution (Advanced)

Use PyInstaller to create standalone executable:
```bash
pip install pyinstaller
pyinstaller --onefile --add-data "book_triage;book_triage" book_triage/cli.py
```

## 🔧 Required Setup for Recipients

### Prerequisites:
- **Python 3.12+** (from python.org)
- **OpenAI API Key** (from openai.com)
- **Tesseract OCR** (optional, for local image processing)

### Environment Setup:
1. Copy `.env.example` to `.env`
2. Edit `.env` and add: `OPENAI_API_KEY=your_key_here`
3. For Japanese OCR: Install Tesseract with Japanese support

## 🎯 Recommended Distribution Method

**For non-technical users:**
- Use Option 1 (Complete Folder)
- Include detailed SETUP_INSTRUCTIONS.md
- Provide your contact for support

**For developers:**
- Use Option 2 (GitHub Repository)
- Include development setup instructions
- Add contribution guidelines

## 📋 Checklist Before Distribution

- [ ] Test all batch files work
- [ ] Verify README is clear and complete
- [ ] Include sample data (sample_books.csv)
- [ ] Create .env.example with all required variables
- [ ] Test installation on clean system
- [ ] Document all dependencies
- [ ] Include troubleshooting section 