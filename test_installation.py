#!/usr/bin/env python3
"""
Installation Test Script for Book Triage
Run this script to verify your installation is working correctly.
"""

import sys
import subprocess
import tempfile
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"Testing: {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    """Run installation tests."""
    print("🧪 Book Triage Installation Test")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Import book_triage module
    total_tests += 1
    try:
        import book_triage
        print("✅ Import book_triage module - PASSED")
        tests_passed += 1
    except ImportError as e:
        print(f"❌ Import book_triage module - FAILED: {e}")
    
    # Test 2: CLI help command
    total_tests += 1
    if run_command("python -m book_triage --help", "CLI help command"):
        tests_passed += 1
    
    # Test 3: Create sample CSV
    total_tests += 1
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        if run_command(f"python -m book_triage create-csv {tmp_path} --sample", "Create sample CSV"):
            tests_passed += 1
            # Verify file was created
            if os.path.exists(tmp_path):
                print("✅ CSV file created successfully")
            else:
                print("❌ CSV file was not created")
                tests_passed -= 1
    finally:
        # Clean up
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
    
    # Test 4: Info command
    total_tests += 1
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # Create a test CSV first
        subprocess.run(f"python -m book_triage create-csv {tmp_path} --sample", shell=True, capture_output=True)
        if run_command(f"python -m book_triage info {tmp_path}", "Info command"):
            tests_passed += 1
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
    
    # Test 5: Check dependencies
    total_tests += 1
    required_modules = ['fastapi', 'pandas', 'typer', 'uvicorn', 'openai']
    deps_ok = True
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            print(f"❌ Missing dependency: {module}")
            deps_ok = False
    
    if deps_ok:
        print("✅ All dependencies available - PASSED")
        tests_passed += 1
    else:
        print("❌ Missing dependencies - FAILED")
    
    # Results
    print("\n" + "=" * 50)
    print(f"🎯 Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Book Triage is ready to use.")
        print("\nNext steps:")
        print("1. Create a CSV file: python -m book_triage create-csv books.csv --sample")
        print("2. Start web interface: python -m book_triage web books.csv")
        print("3. Open http://localhost:8000 in your browser")
        return True
    else:
        print("❌ Some tests failed. Please check the installation.")
        print("\nTroubleshooting:")
        print("1. Make sure you ran: pip install -e .")
        print("2. Check that all dependencies are installed")
        print("3. Try running the failed commands manually")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 