#!/usr/bin/env python3
"""
Simple compatibility test for Book Triage
Tests basic functionality across Windows, macOS, and Linux
"""

import sys
import platform
import subprocess
from pathlib import Path

def test_python_version():
    """Test Python version compatibility"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 12:
        print("✅ Python version:", sys.version)
        return True
    else:
        print("❌ Python version:", sys.version)
        print("   Requires Python 3.12 or higher")
        return False

def test_core_imports():
    """Test importing core dependencies"""
    imports = [
        "pandas", "fastapi", "uvicorn", "typer", "PIL", 
        "pytesseract", "openai", "dotenv", "tqdm", "slowapi"
    ]
    
    passed = 0
    for module in imports:
        try:
            __import__(module)
            print(f"✅ {module}")
            passed += 1
        except ImportError as e:
            print(f"❌ {module}: {e}")
    
    return passed == len(imports)

def test_book_triage_imports():
    """Test Book Triage module imports"""
    if not Path("book_triage").exists():
        print("❌ book_triage directory not found")
        return False
    
    modules = [
        "book_triage.core",
        "book_triage.api", 
        "book_triage.cli",
        "book_triage.vision",
        "book_triage.security"
    ]
    
    passed = 0
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
            passed += 1
        except Exception as e:
            print(f"❌ {module}: {e}")
    
    return passed == len(modules)

def test_platform_specific():
    """Test platform-specific functionality"""
    system = platform.system()
    print(f"Platform: {system} {platform.release()}")
    
    if system == "Windows":
        try:
            import colorama
            print("✅ Windows: colorama available")
        except ImportError:
            print("⚠️  Windows: colorama not found (optional)")
        
        try:
            # Test for python-magic-bin (Windows version)
            import magic
            print("✅ Windows: python-magic available")
        except ImportError:
            print("⚠️  Windows: python-magic not found")
    
    elif system in ["Linux", "Darwin"]:
        try:
            import magic
            print(f"✅ {system}: python-magic available")
        except ImportError:
            print(f"⚠️  {system}: python-magic not found")
    
    return True

def test_cli_basic():
    """Test basic CLI functionality"""
    try:
        result = subprocess.run([
            sys.executable, "-m", "book_triage.cli", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and "Usage:" in result.stdout:
            print("✅ CLI: Basic functionality works")
            return True
        else:
            print("❌ CLI: Basic test failed")
            return False
    except Exception as e:
        print(f"❌ CLI: {e}")
        return False

def main():
    """Run all compatibility tests"""
    print("🚀 Book Triage - Platform Compatibility Test")
    print("=" * 50)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python: {sys.version}")
    print("=" * 50)
    
    tests = [
        ("Python Version", test_python_version),
        ("Core Dependencies", test_core_imports),
        ("Book Triage Modules", test_book_triage_imports),
        ("Platform-Specific", test_platform_specific),
        ("CLI Basic Test", test_cli_basic),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Book Triage is compatible with this platform.")
        status = "EXCELLENT"
    elif passed >= total * 0.8:
        print("✅ Most tests passed. Minor issues may exist.")
        status = "GOOD"
    elif passed >= total * 0.6:
        print("⚠️  Some issues found. Check missing dependencies.")
        status = "ACCEPTABLE"
    else:
        print("❌ Major compatibility issues found.")
        status = "POOR"
    
    # Save results
    report_file = f"compatibility_test_{platform.system().lower()}.txt"
    with open(report_file, "w") as f:
        f.write(f"Book Triage Compatibility Test Results\n")
        f.write(f"Platform: {platform.system()} {platform.release()}\n")
        f.write(f"Python: {sys.version}\n")
        f.write(f"Status: {status}\n")
        f.write(f"Tests Passed: {passed}/{total}\n")
    
    print(f"📄 Report saved: {report_file}")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 