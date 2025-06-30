#!/usr/bin/env python3
"""
Simple Chaos Engineering Test for Book Triage Application

This script tests various failure scenarios without complex server management.
"""

import time
import threading
import requests
from io import BytesIO
from PIL import Image


def test_server_running(base_url="http://localhost:8000"):
    """Check if server is running."""
    try:
        response = requests.get(f"{base_url}/health", timeout=3)
        return response.status_code == 200
    except:
        return False


def create_large_file(size_mb=12):
    """Create a large dummy file."""
    return b"X" * (size_mb * 1024 * 1024)


def test_scan_unauthorized():
    """Test /scan endpoint requires authentication."""
    try:
        response = requests.post("http://localhost:8000/scan", timeout=5)
        return response.status_code == 401
    except:
        return False


def test_rate_limiting():
    """Test rate limiting with 100 burst requests to /books."""
    results = []
    
    def make_request():
        try:
            response = requests.get("http://localhost:8000/books", timeout=2)
            results.append(response.status_code)
        except:
            results.append(0)
    
    # Launch 100 concurrent requests
    threads = []
    for _ in range(100):
        t = threading.Thread(target=make_request)
        threads.append(t)
        t.start()
    
    # Wait for all threads
    for t in threads:
        t.join(timeout=5)
    
    success_count = sum(1 for code in results if code == 200)
    rate_limited_count = sum(1 for code in results if code == 429)
    
    # Should have some 200s initially, then 429s when rate limited
    return success_count > 0 and rate_limited_count > 0


def test_large_file_upload():
    """Test large file upload rejection."""
    try:
        large_file = create_large_file(12)  # 12MB
        response = requests.post(
            "http://localhost:8000/upload_photo",
            files={"file": ("large.jpg", large_file, "image/jpeg")},
            timeout=15
        )
        return response.status_code == 413
    except:
        return False


def test_security_headers():
    """Test security headers presence."""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        
        required_headers = {
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "same-origin"
        }
        
        for header, expected_value in required_headers.items():
            if header not in response.headers:
                return False
            if response.headers[header] != expected_value:
                return False
        
        return True
    except:
        return False


def run_chaos_tests():
    """Run all chaos tests."""
    print("🔥 Simple Chaos Engineering Test 🔥")
    print("=" * 40)
    
    if not test_server_running():
        print("❌ Server not running at http://localhost:8000")
        print("💡 Start with: python -m uvicorn book_triage.api:app --reload")
        return
    
    print("✅ Server detected, running tests...")
    
    tests = [
        ("Unauthorized /scan → 401", test_scan_unauthorized),
        ("Burst requests rate limiting", test_rate_limiting),
        ("Large file upload → 413", test_large_file_upload),
        ("Security headers present", test_security_headers),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Testing {test_name}...")
        try:
            result = test_func()
            results.append(result)
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status}")
        except Exception as e:
            results.append(False)
            print(f"  ❌ FAIL ({e})")
        time.sleep(1)
    
    # Summary
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print("\n" + "=" * 40)
    print("🔥 CHAOS TEST SUMMARY 🔥")
    print("=" * 40)
    print(f"PASSED: {passed}/{total}")
    print(f"SUCCESS RATE: {success_rate:.1f}%")
    
    if success_rate >= 90:
        grade = "A+"
        print("🎉 EXCELLENT! Chaos-resistant!")
    elif success_rate >= 75:
        grade = "A"
        print("✅ GOOD! Strong security!")
    elif success_rate >= 50:
        grade = "B"
        print("⚠️ FAIR! Needs improvement!")
    else:
        grade = "F"
        print("💥 POOR! Critical issues!")
    
    print(f"🏆 GRADE: {grade}")


if __name__ == "__main__":
    run_chaos_tests() 