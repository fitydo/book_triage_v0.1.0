# Windows Installation Guide for Book Triage

This guide provides step-by-step instructions for installing Book Triage on Windows systems.

## Prerequisites

1. **Python 3.12+** - Download from [python.org](https://www.python.org/downloads/)
2. **Git** - Download from [git-scm.com](https://git-scm.com/download/win)
3. **PowerShell** or **Command Prompt**

## Installation Steps

### Method 1: PowerShell/Command Prompt Installation

1. **Open PowerShell as Administrator** (recommended) or Command Prompt

2. **Navigate to your desired directory:**
   ```powershell
   cd C:\Users\%USERNAME%\Documents
   # Or create a projects directory
   mkdir projects
   cd projects
   ```

3. **Clone the repository:**
   ```powershell
   git clone https://github.com/fitydo/book_triage_v0.1.0.git
   cd book_triage_v0.1.0
   ```

4. **If git clone fails with Zone.Identifier errors, try:**
   ```powershell
   # Alternative: Download as ZIP
   # Go to https://github.com/fitydo/book_triage_v0.1.0
   # Click "Code" -> "Download ZIP"
   # Extract to C:\Users\%USERNAME%\Documents\book_triage_v0.1.0
   
   # Or use git with core.protectNTFS disabled (temporary fix)
   git clone -c core.protectNTFS=false https://github.com/fitydo/book_triage_v0.1.0.git
   cd book_triage_v0.1.0
   ```

5. **Install Python dependencies:**
   ```powershell
   pip install -e .
   ```

6. **Set up environment (Required for web interface):**
   ```powershell
   # Create .env file with authentication credentials
   echo BOOK_USER=admin > .env
   echo BOOK_PASS=password >> .env
   
   # Optional: Add OpenAI API key for OCR features
   # echo OPENAI_API_KEY=your_openai_key_here >> .env
   ```

7. **Verify installation:**
   ```powershell
   python -m book_triage --help
   ```

### Method 2: Using Windows Subsystem for Linux (WSL)

If you have WSL installed:

1. **Open WSL terminal**
2. **Follow the Linux installation steps:**
   ```bash
   git clone https://github.com/fitydo/book_triage_v0.1.0.git
   cd book_triage_v0.1.0
   pip install -e .
   python -m book_triage --help
   ```

### Method 3: Using the Windows Distribution Package

1. **Navigate to the Windows distribution:**
   ```powershell
   cd distributions\windows
   ```

2. **Run the Windows batch installer:**
   ```powershell
   .\install.bat
   ```

3. **Start Book Triage:**
   ```powershell
   .\book_triage.bat
   ```

## Troubleshooting Windows Issues

### Issue 1: "Zone.Identifier" file errors during git clone

**Problem:** Git clone fails with invalid path errors for Zone.Identifier files.

**Solution:**
```powershell
# Option 1: Use git with NTFS protection disabled
git clone -c core.protectNTFS=false https://github.com/fitydo/book_triage_v0.1.0.git

# Option 2: Download as ZIP file instead
# Go to GitHub, click "Code" -> "Download ZIP"
```

### Issue 2: "Neither 'setup.py' nor 'pyproject.toml' found"

**Problem:** The git checkout failed, so the Python project files aren't present.

**Solution:**
```powershell
# Check git status
git status

# Restore the working tree
git restore --source=HEAD :/

# Or re-clone with the fix
git clone -c core.protectNTFS=false https://github.com/fitydo/book_triage_v0.1.0.git
```

### Issue 3: "No module named book_triage"

**Problem:** Installation didn't complete successfully.

**Solution:**
```powershell
# Make sure you're in the right directory
cd book_triage_v0.1.0

# Check if pyproject.toml exists
dir pyproject.toml

# Install dependencies
pip install -e .

# If still failing, try:
pip install --user -e .
```

### Issue 4: Permission errors

**Problem:** Access denied errors during installation.

**Solution:**
```powershell
# Run PowerShell as Administrator
# Or use user installation
pip install --user -e .
```

### Issue 5: "The api_key client option must be set" error

**Problem:** Web interface fails to start with OpenAI API key error.

**Solution:**
The OpenAI API key is **optional** and only needed for advanced OCR features. You can run Book Triage without it:

```powershell
# Option 1: Skip OCR features (recommended for basic use)
# Just ensure you have the basic authentication set up:
echo BOOK_USER=admin > .env
echo BOOK_PASS=password >> .env

# Option 2: Add OpenAI API key for OCR features
# Get your key from: https://platform.openai.com/api-keys
echo OPENAI_API_KEY=your_actual_key_here >> .env
```

**Note:** Most Book Triage features work without OpenAI API key. OCR is only needed for scanning physical book images.

### Issue 6: Tesseract OCR not found

**Problem:** OCR features don't work.

**Solution:**
1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default location: `C:\Program Files\Tesseract-OCR\`
3. Add to PATH or set environment variable:
   ```powershell
   $env:PATH += ";C:\Program Files\Tesseract-OCR"
   ```

## Testing Your Installation

1. **Run the installation test:**
   ```powershell
   python test_installation.py
   ```

2. **Expected output:**
   ```
   🎯 Results: 5/5 tests passed
   🎉 All tests passed! Book Triage is ready to use.
   ```

## Quick Start (Windows)

### Option 1: Automated Setup (Recommended)

1. **Run the quick start script:**
   ```powershell
   .\quick_start_windows.bat
   ```

   This will:
   - Create a `.env` file with default credentials
   - Generate sample data
   - Start the web interface
   - Open at http://localhost:8000

### Option 2: Manual Setup

1. **Create environment file:**
   ```powershell
   # Create .env file
   echo BOOK_USER=admin > .env
   echo BOOK_PASS=password >> .env
   ```

2. **Create sample data:**
   ```powershell
   python -m book_triage create-csv books.csv --sample
   ```

3. **Start web interface:**
   ```powershell
   python -m book_triage web books.csv
   ```

4. **Open in browser:**
   ```
   http://localhost:8000
   Login: admin / password
   ```

## Windows-Specific Features

- **Batch files** in `distributions/windows/` for easy startup
- **Windows installer** script for automated setup
- **PowerShell scripts** for advanced users
- **Native Windows paths** support

## Getting Help

- **GitHub Issues:** https://github.com/fitydo/book_triage_v0.1.0/issues
- **Run diagnostics:** `python test_installation.py`
- **Check logs:** Look for error messages in the terminal output

## Notes for Windows Users

- Use **PowerShell** (recommended) or **Command Prompt**
- Some antivirus software may flag the installation - this is normal
- If using corporate Windows, you may need IT approval for Python packages
- The web interface works best with **Chrome** or **Edge** browsers 