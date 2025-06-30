#!/usr/bin/env python3
"""
Simple cross-platform distribution builder for Book Triage
Creates platform-specific packages for Windows 11, macOS, and Linux
"""

import os
import sys
import shutil
import zipfile
import tarfile
from pathlib import Path

def get_version():
    """Get version from pyproject.toml"""
    try:
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            content = f.read()
            for line in content.split('\n'):
                if line.strip().startswith('version = '):
                    return line.split('"')[1]
    except Exception:
        return "0.1.0"

def create_base_distribution(platform_name):
    """Create base distribution for a platform"""
    print(f"Creating {platform_name} distribution...")
    
    dist_dir = Path(f"distributions/{platform_name}")
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy core files
    files_to_copy = [
        "book_triage/",
        "examples/",
        "scripts/",
        "tests/",
        "README.md",
        "LICENSE",
        "pyproject.toml"
    ]
    
    # Copy .env.example if it exists
    if Path(".env.example").exists():
        files_to_copy.append(".env.example")
    elif Path("book_triage/env_example.txt").exists():
        files_to_copy.append("book_triage/env_example.txt")
    
    for item in files_to_copy:
        src = Path(item)
        if src.exists():
            if src.is_dir():
                shutil.copytree(src, dist_dir / src.name, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dist_dir / src.name)
    
    return dist_dir

def create_windows_package():
    """Create Windows package"""
    dist_dir = create_base_distribution("windows")
    
    # Create simple Windows installer
    installer = dist_dir / "install.bat"
    with open(installer, "w", encoding="utf-8") as f:
        f.write("""@echo off
echo Book Triage Windows Installation
echo ================================
echo.
echo Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -e .
echo.
echo Setup complete!
echo To start: python -m uvicorn book_triage.api:app --reload
echo.
pause
""")
    
    # Create startup script
    starter = dist_dir / "start.bat"
    with open(starter, "w", encoding="utf-8") as f:
        f.write("""@echo off
echo Starting Book Triage...
echo Open browser to: http://localhost:8000
python -m uvicorn book_triage.api:app --host 0.0.0.0 --port 8000
pause
""")
    
    # Create README
    readme = dist_dir / "README_WINDOWS.txt"
    with open(readme, "w", encoding="utf-8") as f:
        f.write("""Book Triage - Windows Installation

Requirements:
- Python 3.12 or higher
- Internet connection for dependencies

Installation:
1. Double-click install.bat
2. Wait for installation to complete
3. Double-click start.bat to run the application

Troubleshooting:
- If Python is not found, install from python.org
- Run as Administrator if permission errors occur
""")
    
    # Create ZIP
    version = get_version()
    zip_path = f"distributions/book-triage-{version}-windows.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(dist_dir.parent)
                zipf.write(file_path, arcname)
    
    print(f"Windows package created: {zip_path}")
    return zip_path

def create_linux_package():
    """Create Linux package"""
    dist_dir = create_base_distribution("linux")
    
    # Create installer script
    installer = dist_dir / "install.sh"
    with open(installer, "w", encoding="utf-8") as f:
        f.write("""#!/bin/bash
echo "Book Triage Linux Installation"
echo "=============================="
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.12+"
    exit 1
fi

echo "Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y python3-pip libmagic1 tesseract-ocr
elif command -v yum &> /dev/null; then
    sudo yum install -y python3-pip file-devel tesseract
fi

echo "Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -e .

echo
echo "Setup complete!"
echo "To start: python3 -m uvicorn book_triage.api:app --reload"
echo
""")
    os.chmod(installer, 0o755)
    
    # Create startup script
    starter = dist_dir / "start.sh"
    with open(starter, "w", encoding="utf-8") as f:
        f.write("""#!/bin/bash
echo "Starting Book Triage..."
echo "Open browser to: http://localhost:8000"
python3 -m uvicorn book_triage.api:app --host 0.0.0.0 --port 8000
""")
    os.chmod(starter, 0o755)
    
    # Create README
    readme = dist_dir / "README_LINUX.txt"
    with open(readme, "w", encoding="utf-8") as f:
        f.write("""Book Triage - Linux Installation

Requirements:
- Python 3.12 or higher
- sudo access for system dependencies

Installation:
1. chmod +x install.sh
2. ./install.sh
3. ./start.sh to run the application

Tested on:
- Ubuntu 20.04+
- CentOS 8+
- Debian 11+
""")
    
    # Create TAR.GZ
    version = get_version()
    tar_path = f"distributions/book-triage-{version}-linux.tar.gz"
    with tarfile.open(tar_path, 'w:gz') as tar:
        tar.add(dist_dir, arcname=f"book-triage-{version}-linux")
    
    print(f"Linux package created: {tar_path}")
    return tar_path

def create_macos_package():
    """Create macOS package"""
    dist_dir = create_base_distribution("macos")
    
    # Create installer script
    installer = dist_dir / "install.sh"
    with open(installer, "w", encoding="utf-8") as f:
        f.write("""#!/bin/bash
echo "Book Triage macOS Installation"
echo "=============================="
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.12+"
    exit 1
fi

echo "Installing dependencies..."
if command -v brew &> /dev/null; then
    brew install libmagic tesseract
else
    echo "Warning: Homebrew not found. Install manually:"
    echo "  libmagic and tesseract"
fi

echo "Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -e .

echo
echo "Setup complete!"
echo "To start: python3 -m uvicorn book_triage.api:app --reload"
echo
""")
    os.chmod(installer, 0o755)
    
    # Create startup script
    starter = dist_dir / "start.sh"
    with open(starter, "w", encoding="utf-8") as f:
        f.write("""#!/bin/bash
echo "Starting Book Triage..."
echo "Open browser to: http://localhost:8000"
python3 -m uvicorn book_triage.api:app --host 0.0.0.0 --port 8000
""")
    os.chmod(starter, 0o755)
    
    # Create README
    readme = dist_dir / "README_MACOS.txt"
    with open(readme, "w", encoding="utf-8") as f:
        f.write("""Book Triage - macOS Installation

Requirements:
- Python 3.12 or higher
- Homebrew (recommended)

Installation:
1. chmod +x install.sh
2. ./install.sh
3. ./start.sh to run the application

Works on:
- macOS 10.15+ (Intel & Apple Silicon)
""")
    
    # Create ZIP
    version = get_version()
    zip_path = f"distributions/book-triage-{version}-macos.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(dist_dir.parent)
                zipf.write(file_path, arcname)
    
    print(f"macOS package created: {zip_path}")
    return zip_path

def main():
    """Create all distributions"""
    print("Book Triage Distribution Builder")
    print("=" * 40)
    
    # Clean old distributions
    if Path("distributions").exists():
        shutil.rmtree("distributions")
    
    packages = []
    
    try:
        packages.append(create_windows_package())
        packages.append(create_linux_package())
        packages.append(create_macos_package())
        
        print("\n" + "=" * 40)
        print("Distribution creation complete!")
        print("\nCreated packages:")
        for pkg in packages:
            if pkg:
                size = Path(pkg).stat().st_size / (1024 * 1024)
                print(f"  {pkg} ({size:.1f}MB)")
        
        print("\nReady for GitHub release!")
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 