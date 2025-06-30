#!/usr/bin/env python3
"""
Cross-platform distribution builder for Book Triage
Creates platform-specific packages for Windows 11, macOS, and Linux
"""

import os
import sys
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
import json
import platform

def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result"""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(
        cmd, 
        cwd=cwd, 
        capture_output=True, 
        text=True, 
        check=check,
        shell=True if isinstance(cmd, str) else False
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        if check:
            raise subprocess.CalledProcessError(result.returncode, cmd)
    return result

def get_version():
    """Get version from pyproject.toml"""
    try:
        with open("pyproject.toml", "r") as f:
            content = f.read()
            for line in content.split('\n'):
                if line.strip().startswith('version = '):
                    return line.split('"')[1]
    except Exception:
        return "0.1.0"

def create_requirements_txt():
    """Create requirements.txt from pyproject.toml"""
    print("Creating requirements.txt...")
    try:
        result = run_command([sys.executable, "-m", "pip", "freeze"], check=False)
        with open("requirements.txt", "w") as f:
            f.write(result.stdout)
        print("✓ requirements.txt created")
    except Exception as e:
        print(f"Warning: Could not create requirements.txt: {e}")

def build_wheel():
    """Build Python wheel"""
    print("Building Python wheel...")
    try:
        run_command([sys.executable, "-m", "build"])
        print("✓ Wheel built successfully")
        return True
    except Exception as e:
        print(f"Error building wheel: {e}")
        return False

def create_windows_distribution():
    """Create Windows 11 distribution package"""
    print("\n🪟 Creating Windows 11 distribution...")
    
    dist_dir = Path("distributions/windows")
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy core files
    files_to_copy = [
        "book_triage/",
        "examples/",
        "scripts/",
        "tests/",
        "README.md",
        "LICENSE",
        "pyproject.toml",
        ".env.example"
    ]
    
    for item in files_to_copy:
        src = Path(item)
        if src.exists():
            if src.is_dir():
                shutil.copytree(src, dist_dir / src.name, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dist_dir / src.name)
    
    # Create Windows-specific installer script
    installer_script = dist_dir / "install_windows.bat"
    with open(installer_script, "w") as f:
        f.write("""@echo off
echo Book Triage - Windows 11 Installation
echo ====================================

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.12+ is required but not found.
    echo Please install Python from https://python.org/downloads/
    pause
    exit /b 1
)

echo Installing Book Triage...
python -m pip install --upgrade pip
python -m pip install -e .

echo Setting up environment...
if not exist .env copy .env.example .env

echo Creating desktop shortcut...
if exist scripts\\create_shortcut.bat call scripts\\create_shortcut.bat

echo.
echo ✓ Installation complete!
echo.
echo To start Book Triage:
echo   Web interface: python -m uvicorn book_triage.api:app --reload
echo   CLI: python -m book_triage.cli --help
echo.
pause
""")
    
    # Create Windows startup script
    startup_script = dist_dir / "start_book_triage_windows.bat"
    with open(startup_script, "w") as f:
        f.write("""@echo off
title Book Triage - Windows 11
echo Starting Book Triage Web Interface...
echo Open your browser to: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python -m uvicorn book_triage.api:app --host 0.0.0.0 --port 8000 --reload
pause
""")
    
    # Create Windows requirements
    win_requirements = dist_dir / "requirements_windows.txt"
    with open(win_requirements, "w", encoding="utf-8") as f:
        f.write("""# Book Triage - Windows 11 Requirements
openai>=1.0.0
pandas>=2.0.0
python-dotenv>=1.0.0
tqdm>=4.65.0
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pillow>=10.0.0
pytesseract>=0.3.10
typer>=0.9.0
python-multipart>=0.0.6
slowapi>=0.1.8
python-magic-bin>=0.4.14
colorama>=0.4.6
pywin32>=306
wmi>=1.5.1
""")
    
    # Create ZIP package
    version = get_version()
    zip_path = f"distributions/book-triage-{version}-windows11.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(dist_dir)
                zipf.write(file_path, f"book-triage-{version}-windows11/{arcname}")
    
    print(f"✓ Windows 11 distribution created: {zip_path}")
    return zip_path

def create_linux_distribution():
    """Create Linux distribution package"""
    print("\n🐧 Creating Linux distribution...")
    
    dist_dir = Path("distributions/linux")
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy core files
    files_to_copy = [
        "book_triage/",
        "examples/", 
        "scripts/",
        "tests/",
        "README.md",
        "LICENSE",
        "pyproject.toml",
        ".env.example"
    ]
    
    for item in files_to_copy:
        src = Path(item)
        if src.exists():
            if src.is_dir():
                shutil.copytree(src, dist_dir / src.name, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dist_dir / src.name)
    
    # Create Linux installer script
    installer_script = dist_dir / "install_linux.sh"
    with open(installer_script, "w") as f:
        f.write("""#!/bin/bash
echo "Book Triage - Linux Installation"
echo "================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3.12+ is required but not found."
    echo "Install with: sudo apt-get install python3.12 python3.12-pip"
    exit 1
fi

# Check system dependencies
echo "Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y libmagic1 tesseract-ocr python3-dev
elif command -v yum &> /dev/null; then
    sudo yum install -y file-devel tesseract
elif command -v pacman &> /dev/null; then
    sudo pacman -S --noconfirm file tesseract
fi

echo "Installing Book Triage..."
python3 -m pip install --upgrade pip
python3 -m pip install -e .

echo "Setting up environment..."
[ ! -f .env ] && cp .env.example .env

echo ""
echo "✓ Installation complete!"
echo ""
echo "To start Book Triage:"
echo "  Web interface: python3 -m uvicorn book_triage.api:app --reload"
echo "  CLI: python3 -m book_triage.cli --help"
echo ""
""")
    os.chmod(installer_script, 0o755)
    
    # Create Linux startup script
    startup_script = dist_dir / "start_book_triage_linux.sh"
    with open(startup_script, "w") as f:
        f.write("""#!/bin/bash
echo "Starting Book Triage Web Interface..."
echo "Open your browser to: http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""
python3 -m uvicorn book_triage.api:app --host 0.0.0.0 --port 8000 --reload
""")
    os.chmod(startup_script, 0o755)
    
    # Create Linux requirements
    linux_requirements = dist_dir / "requirements_linux.txt"
    with open(linux_requirements, "w") as f:
        f.write("""# Book Triage - Linux Requirements
openai>=1.0.0
pandas>=2.0.0
python-dotenv>=1.0.0
tqdm>=4.65.0
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pillow>=10.0.0
pytesseract>=0.3.10
typer>=0.9.0
python-multipart>=0.0.6
slowapi>=0.1.8
python-magic>=0.4.27
""")
    
    # Create TAR.GZ package
    version = get_version()
    tar_path = f"distributions/book-triage-{version}-linux.tar.gz"
    shutil.make_archive(
        tar_path.replace('.tar.gz', ''), 
        'gztar', 
        'distributions', 
        'linux'
    )
    
    print(f"✓ Linux distribution created: {tar_path}")
    return tar_path

def create_macos_distribution():
    """Create macOS distribution package"""
    print("\n🍎 Creating macOS distribution...")
    
    dist_dir = Path("distributions/macos")
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy core files
    files_to_copy = [
        "book_triage/",
        "examples/",
        "scripts/",
        "tests/",
        "README.md",
        "LICENSE", 
        "pyproject.toml",
        ".env.example"
    ]
    
    for item in files_to_copy:
        src = Path(item)
        if src.exists():
            if src.is_dir():
                shutil.copytree(src, dist_dir / src.name, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dist_dir / src.name)
    
    # Create macOS installer script
    installer_script = dist_dir / "install_macos.sh"
    with open(installer_script, "w") as f:
        f.write("""#!/bin/bash
echo "Book Triage - macOS Installation"
echo "================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3.12+ is required but not found."
    echo "Install with: brew install python@3.12"
    echo "Or download from: https://python.org/downloads/"
    exit 1
fi

# Check Homebrew and install dependencies
if command -v brew &> /dev/null; then
    echo "Installing system dependencies..."
    brew install libmagic tesseract
else
    echo "Warning: Homebrew not found. Please install manually:"
    echo "  libmagic: for file type detection"
    echo "  tesseract: for OCR functionality"
fi

echo "Installing Book Triage..."
python3 -m pip install --upgrade pip
python3 -m pip install -e .

echo "Setting up environment..."
[ ! -f .env ] && cp .env.example .env

echo ""
echo "✓ Installation complete!"
echo ""
echo "To start Book Triage:"
echo "  Web interface: python3 -m uvicorn book_triage.api:app --reload"
echo "  CLI: python3 -m book_triage.cli --help"
echo ""
""")
    os.chmod(installer_script, 0o755)
    
    # Create macOS startup script
    startup_script = dist_dir / "start_book_triage_macos.sh"
    with open(startup_script, "w") as f:
        f.write("""#!/bin/bash
echo "Starting Book Triage Web Interface..."
echo "Open your browser to: http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""
python3 -m uvicorn book_triage.api:app --host 0.0.0.0 --port 8000 --reload
""")
    os.chmod(startup_script, 0o755)
    
    # Create macOS requirements
    macos_requirements = dist_dir / "requirements_macos.txt"
    with open(macos_requirements, "w") as f:
        f.write("""# Book Triage - macOS Requirements
openai>=1.0.0
pandas>=2.0.0
python-dotenv>=1.0.0
tqdm>=4.65.0
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pillow>=10.0.0
pytesseract>=0.3.10
typer>=0.9.0
python-multipart>=0.0.6
slowapi>=0.1.8
python-magic>=0.4.27
""")
    
    # Create ZIP package
    version = get_version()
    zip_path = f"distributions/book-triage-{version}-macos.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(dist_dir)
                zipf.write(file_path, f"book-triage-{version}-macos/{arcname}")
    
    print(f"✓ macOS distribution created: {zip_path}")
    return zip_path

def create_universal_distribution():
    """Create universal source distribution"""
    print("\n🌍 Creating universal source distribution...")
    
    dist_dir = Path("distributions/universal")
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy all files
    files_to_copy = [
        "book_triage/",
        "examples/",
        "scripts/", 
        "tests/",
        "docs/",
        ".github/",
        "README.md",
        "LICENSE",
        "pyproject.toml",
        ".env.example",
        ".gitignore"
    ]
    
    for item in files_to_copy:
        src = Path(item)
        if src.exists():
            if src.is_dir():
                shutil.copytree(src, dist_dir / src.name, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dist_dir / src.name)
    
    # Create universal installer
    installer_script = dist_dir / "install.py"
    with open(installer_script, "w") as f:
        f.write("""#!/usr/bin/env python3
'''
Universal Book Triage Installer
Detects platform and installs appropriate dependencies
'''

import sys
import subprocess
import platform
import os

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def install_book_triage():
    print("Book Triage - Universal Installer")
    print("=================================")
    
    # Detect platform
    system = platform.system().lower()
    print(f"Detected platform: {system}")
    
    # Install base package
    print("Installing Book Triage...")
    result = run_cmd(f"{sys.executable} -m pip install -e .")
    if result.returncode != 0:
        print(f"Error installing: {result.stderr}")
        return False
    
    # Platform-specific setup
    if system == "windows":
        print("Installing Windows-specific dependencies...")
        run_cmd(f"{sys.executable} -m pip install python-magic-bin pywin32 colorama")
    elif system in ["linux", "darwin"]:
        print("Installing Unix-specific dependencies...")
        run_cmd(f"{sys.executable} -m pip install python-magic")
    
    # Setup environment
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            import shutil
            shutil.copy(".env.example", ".env")
            print("Created .env file from template")
    
    print("\\n✓ Installation complete!")
    print("\\nTo start Book Triage:")
    print("  Web interface: python -m uvicorn book_triage.api:app --reload")
    print("  CLI: python -m book_triage.cli --help")
    
    return True

if __name__ == "__main__":
    install_book_triage()
""")
    
    # Create ZIP package
    version = get_version()
    zip_path = f"distributions/book-triage-{version}-universal.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(dist_dir)
                zipf.write(file_path, f"book-triage-{version}-universal/{arcname}")
    
    print(f"✓ Universal distribution created: {zip_path}")
    return zip_path

def create_release_notes():
    """Create release notes for all distributions"""
    version = get_version()
    notes_path = "distributions/RELEASE_NOTES.md"
    
    with open(notes_path, "w") as f:
        f.write(f"""# Book Triage v{version} - Distribution Release

## 📦 Available Distributions

### Windows 11 (`book-triage-{version}-windows11.zip`)
- **Compatibility**: Windows 10/11 with Python 3.12+
- **Includes**: Windows batch scripts, desktop shortcut creator
- **Dependencies**: Automatically handles Windows-specific libraries
- **Installation**: Run `install_windows.bat`
- **Startup**: Run `start_book_triage_windows.bat`

### Linux (`book-triage-{version}-linux.tar.gz`)
- **Compatibility**: Ubuntu 20.04+, CentOS 8+, Arch Linux
- **Includes**: Shell scripts, system dependency installer
- **Dependencies**: Automatically installs libmagic, tesseract
- **Installation**: Run `./install_linux.sh`
- **Startup**: Run `./start_book_triage_linux.sh`

### macOS (`book-triage-{version}-macos.zip`)
- **Compatibility**: macOS 10.15+ (Intel/Apple Silicon)
- **Includes**: Shell scripts, Homebrew integration
- **Dependencies**: Installs via Homebrew when available
- **Installation**: Run `./install_macos.sh`
- **Startup**: Run `./start_book_triage_macos.sh`

### Universal Source (`book-triage-{version}-universal.zip`)
- **Compatibility**: Any platform with Python 3.12+
- **Includes**: Complete source code, CI/CD, tests
- **Installation**: Run `python install.py`
- **Best for**: Developers, custom deployments

## 🚀 Quick Start

1. **Download** the appropriate distribution for your platform
2. **Extract** the archive to your desired location
3. **Run the installer** script for your platform
4. **Start the application** using the startup script

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.12 or higher
- **RAM**: 512MB available
- **Disk**: 500MB free space
- **Network**: Internet connection for AI features (optional)

### Recommended Requirements
- **Python**: 3.12+ 
- **RAM**: 2GB available
- **Disk**: 1GB free space
- **OCR**: Tesseract installed for image processing

## 🔧 Manual Installation

If the automated installers don't work, you can install manually:

```bash
# 1. Extract the distribution
unzip book-triage-{version}-[platform].zip
cd book-triage-{version}-[platform]

# 2. Install Python dependencies
pip install -e .

# 3. Copy environment template
cp .env.example .env

# 4. Start the application
python -m uvicorn book_triage.api:app --reload
```

## 🌐 Platform-Specific Notes

### Windows 11
- Requires Microsoft Visual C++ Redistributable
- Windows Defender may flag the installer - this is normal
- Run PowerShell as Administrator for system-wide installation

### Linux
- Requires `sudo` access for system dependencies
- Tested on Ubuntu 20.04+, CentOS 8+, Debian 11+
- Some distributions may need additional packages

### macOS
- Works on both Intel and Apple Silicon Macs
- Homebrew recommended for easy dependency management
- May require "Allow apps downloaded from anywhere" setting

## 🆘 Troubleshooting

### Common Issues

**Python not found**
- Install Python 3.12+ from python.org
- Ensure Python is in your system PATH

**Permission denied**
- Run installer as Administrator (Windows) or with sudo (Linux/macOS)
- Check file permissions: `chmod +x install_*.sh`

**Dependencies fail to install**
- Update pip: `python -m pip install --upgrade pip`
- Install system dependencies manually (see docs)

**OCR not working**
- Install Tesseract: Windows (via installer), Linux (`apt install tesseract-ocr`), macOS (`brew install tesseract`)

### Getting Help

- **Documentation**: See `docs/` folder in any distribution
- **Issues**: https://github.com/fitydo/book_triage_v1.0.0/issues
- **Discussions**: https://github.com/fitydo/book_triage_v1.0.0/discussions

## 🔐 Security

All distributions include the same security features:
- HTTP Basic Authentication
- Rate limiting
- File upload validation
- Security headers
- Input sanitization

Default credentials: `BOOK_USER=admin`, `BOOK_PASS=password`
**⚠️ Change these immediately in production!**

## 📊 Verification

After installation, verify your setup:

```bash
# Test CLI
python -m book_triage.cli --help

# Test web interface
python -m uvicorn book_triage.api:app --reload
# Visit http://localhost:8000

# Run tests
python -m pytest tests/ -v
```

## 🎯 Next Steps

1. **Configure** your environment in `.env`
2. **Add your books** using the web interface or CLI
3. **Set up OCR** for image processing (optional)
4. **Explore examples** in the `examples/` folder
5. **Read documentation** in the `docs/` folder

---

**Book Triage v{version}** - Happy triaging! 📚
""")
    
    print(f"✓ Release notes created: {notes_path}")
    return notes_path

def main():
    """Main distribution builder"""
    print("🚀 Book Triage Cross-Platform Distribution Builder")
    print("=" * 50)
    
    # Verify we're in the right directory
    if not Path("pyproject.toml").exists():
        print("Error: Must run from project root directory")
        return 1
    
    # Clean previous distributions
    if Path("distributions").exists():
        shutil.rmtree("distributions")
    
    # Create requirements.txt
    create_requirements_txt()
    
    # Build wheel
    wheel_success = build_wheel()
    
    distributions = []
    
    try:
        # Create platform-specific distributions
        distributions.append(create_windows_distribution())
        distributions.append(create_linux_distribution())
        distributions.append(create_macos_distribution())
        distributions.append(create_universal_distribution())
        
        # Create release notes
        create_release_notes()
        
        # Summary
        print("\n" + "=" * 50)
        print("🎉 Distribution build complete!")
        print("\nCreated distributions:")
        for dist in distributions:
            if dist:
                size = Path(dist).stat().st_size / (1024 * 1024)  # MB
                print(f"  📦 {dist} ({size:.1f}MB)")
        
        print(f"\n📄 Release notes: distributions/RELEASE_NOTES.md")
        print("\n✅ Ready for GitHub release!")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error creating distributions: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 