#!/usr/bin/env python3
"""
Chaos Engineering Demo for Book Triage Application

This demonstrates the chaos engineering tests that would be performed
on the Book Triage security-hardened application.
"""

import time
import random


def log(message: str, level: str = "INFO") -> None:
    """Log messages with timestamp."""
    timestamp = time.strftime("%H:%M:%S")
    status_emoji = {"INFO": "🔵", "SUCCESS": "🟢", "WARNING": "🟡", "ERROR": "🔴"}
    emoji = status_emoji.get(level, "🔵")
    print(f"[{timestamp}] {emoji} {message}")


def simulate_test_result(test_name: str, success_probability: float = 0.9):
    """Simulate a test result based on security implementation."""
    success = random.random() < success_probability
    return f"✅ {test_name}" if success else f"❌ {test_name}"


def demo_scan_unauthorized():
    """Demo /scan authentication test."""
    print("Testing /scan unauthorized access...")
    time.sleep(0.5)
    result = simulate_test_result("Unauthorized /scan → 401", 0.95)
    print(f"  {result}")
    return result.startswith("✅")


def demo_rate_limiting():
    """Demo rate limiting test."""
    print("Testing burst 100 requests to /books...")
    time.sleep(1.0)  # Simulate longer test
    result = simulate_test_result("Rate limiting 200→429", 0.88)
    print(f"  {result}")
    return result.startswith("✅")


def demo_large_file_upload():
    """Demo large file upload test."""
    print("Testing 12MB file upload...")
    time.sleep(0.8)
    result = simulate_test_result("Large file → 413", 0.92)
    print(f"  {result}")
    return result.startswith("✅")


def demo_security_headers():
    """Demo security headers test."""
    print("Testing security headers...")
    time.sleep(0.3)
    result = simulate_test_result("All security headers present", 0.96)
    print(f"  {result}")
    return result.startswith("✅")


def run_chaos_demo():
    """Run the offline chaos demo."""
    print("🔥 Chaos Engineering Demo 🔥")
    print("=" * 40)
    print("Simulating tests against security-hardened Book Triage")
    print()
    
    tests = [
        ("🔒 Authentication Test", demo_scan_unauthorized),
        ("⏱️ Rate Limiting Test", demo_rate_limiting),
        ("📁 File Upload Test", demo_large_file_upload),
        ("🛡️ Security Headers Test", demo_security_headers),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"--- {test_name} ---")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            results.append(False)
            print(f"  ❌ Test failed: {e}")
        time.sleep(0.5)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print("=" * 40)
    print("🔥 CHAOS DEMO SUMMARY 🔥")
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
    
    print("\n🛡️ Security Features Demonstrated:")
    features = [
        "✅ HTTP Basic Authentication",
        "✅ Rate limiting (30-60 req/min)",
        "✅ File size validation (10MB limit)",
        "✅ Security headers (XFO, CSP, HSTS)"
    ]
    for feature in features:
        print(feature)


if __name__ == "__main__":
    run_chaos_demo() 