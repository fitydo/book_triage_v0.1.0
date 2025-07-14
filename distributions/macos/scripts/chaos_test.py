#!/usr/bin/env python3
"""
Chaos Engineering Script for Book Triage Application

This script performs various chaos experiments to test the resilience
and fault tolerance of the Book Triage FastAPI application.
"""

import asyncio
import os
import random
import signal
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Any

import requests
from PIL import Image
import io


class ChaosEngineer:
    """Chaos engineering test suite for Book Triage application."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        self.server_process = None
        
    def log(self, message: str, level: str = "INFO") -> None:
        """Log messages with timestamp."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def start_server(self) -> bool:
        """Start the Book Triage server."""
        try:
            # Create a minimal CSV for testing
            csv_path = Path("chaos_test_books.csv")
            csv_path.write_text("id,title,url,F,R,A,V,S,P,decision\n")
            
            # Initialize the app directly instead of starting subprocess
            from book_triage.api import initialize_app, app
            initialize_app(csv_path, scan_cost=2)
            
            # Start the server using uvicorn
            import uvicorn
            
            # Run server in background thread
            import threading
            
            def run_server():
                uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            # Wait for server to start
            for i in range(15):
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=2)
                    if response.status_code == 200:
                        self.log("Server started successfully")
                        return True
                except requests.exceptions.RequestException:
                    self.log(f"Waiting for server... ({i+1}/15)")
                    time.sleep(2)
            
            self.log("Failed to start server", "ERROR")
            return False
            
        except Exception as e:
            self.log(f"Error starting server: {e}", "ERROR")
            return False
    
    def stop_server(self) -> None:
        """Stop the Book Triage server."""
        self.log("Server cleanup (daemon thread will stop automatically)")
        
        # Cleanup test files
        for file in ["chaos_test_books.csv"]:
            if Path(file).exists():
                Path(file).unlink()
    
    def create_test_image(self, size_mb: float = 0.1) -> bytes:
        """Create a test image of specified size."""
        # Calculate dimensions for target file size
        target_bytes = int(size_mb * 1024 * 1024)
        width = height = int((target_bytes / 3) ** 0.5)  # RGB = 3 bytes per pixel
        
        image = Image.new('RGB', (width, height), color='red')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG', quality=95)
        return img_bytes.getvalue()
    
    def test_basic_connectivity(self) -> Dict[str, Any]:
        """Test basic server connectivity."""
        self.log("Testing basic connectivity...")
        results = {"test": "basic_connectivity", "passed": 0, "failed": 0, "errors": []}
        
        endpoints = ["/", "/health", "/books"]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code in [200, 401]:  # 401 for protected endpoints
                    results["passed"] += 1
                    self.log(f"✅ {endpoint}: {response.status_code}")
                else:
                    results["failed"] += 1
                    results["errors"].append(f"{endpoint}: unexpected status {response.status_code}")
                    self.log(f"❌ {endpoint}: {response.status_code}", "ERROR")
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"{endpoint}: {str(e)}")
                self.log(f"❌ {endpoint}: {e}", "ERROR")
        
        return results
    
    def test_rate_limiting_chaos(self) -> Dict[str, Any]:
        """Test rate limiting under high load."""
        self.log("Testing rate limiting resilience...")
        results = {"test": "rate_limiting", "passed": 0, "failed": 0, "errors": []}
        
        def make_request(url: str) -> int:
            try:
                response = requests.get(url, timeout=2)
                return response.status_code
            except:
                return 0
        
        # Flood the /books endpoint (30/min limit)
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [
                executor.submit(make_request, f"{self.base_url}/books")
                for _ in range(100)
            ]
            
            status_codes = []
            for future in as_completed(futures, timeout=30):
                try:
                    status_codes.append(future.result())
                except Exception as e:
                    results["errors"].append(f"Request failed: {e}")
        
        # Analyze results
        success_count = sum(1 for code in status_codes if code == 200)
        rate_limited_count = sum(1 for code in status_codes if code == 429)
        
        if rate_limited_count > 0:
            results["passed"] += 1
            self.log(f"✅ Rate limiting working: {success_count} success, {rate_limited_count} rate-limited")
        else:
            results["failed"] += 1
            results["errors"].append("Rate limiting not triggered")
            self.log("❌ Rate limiting not working", "ERROR")
        
        return results
    
    def test_authentication_bypass_attempts(self) -> Dict[str, Any]:
        """Test authentication security."""
        self.log("Testing authentication security...")
        results = {"test": "auth_security", "passed": 0, "failed": 0, "errors": []}
        
        # Test unauthorized access to protected endpoint
        try:
            response = requests.post(f"{self.base_url}/scan", timeout=5)
            if response.status_code == 401:
                results["passed"] += 1
                self.log("✅ Authentication required for /scan")
            else:
                results["failed"] += 1
                results["errors"].append(f"/scan accessible without auth: {response.status_code}")
                self.log(f"❌ /scan bypass: {response.status_code}", "ERROR")
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"/scan test failed: {e}")
        
        # Test with invalid credentials
        try:
            response = requests.post(
                f"{self.base_url}/scan",
                auth=("wrong", "credentials"),
                timeout=5
            )
            if response.status_code == 401:
                results["passed"] += 1
                self.log("✅ Invalid credentials rejected")
            else:
                results["failed"] += 1
                results["errors"].append(f"Invalid creds accepted: {response.status_code}")
                self.log(f"❌ Invalid creds bypass: {response.status_code}", "ERROR")
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"Invalid creds test failed: {e}")
        
        return results
    
    def test_file_upload_chaos(self) -> Dict[str, Any]:
        """Test file upload security and limits."""
        self.log("Testing file upload resilience...")
        results = {"test": "file_upload", "passed": 0, "failed": 0, "errors": []}
        
        # Test oversized file (>10MB)
        try:
            large_file = b"X" * (11 * 1024 * 1024)  # 11MB
            response = requests.post(
                f"{self.base_url}/upload_photo",
                files={"file": ("large.jpg", large_file, "image/jpeg")},
                timeout=10
            )
            if response.status_code == 413:
                results["passed"] += 1
                self.log("✅ Large file rejected (413)")
            else:
                results["failed"] += 1
                results["errors"].append(f"Large file not rejected: {response.status_code}")
                self.log(f"❌ Large file accepted: {response.status_code}", "ERROR")
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"Large file test failed: {e}")
        
        # Test malicious file type
        try:
            malicious_content = b"#!/bin/bash\necho 'malicious'"
            response = requests.post(
                f"{self.base_url}/upload_photo",
                files={"file": ("script.sh", malicious_content, "application/x-sh")},
                timeout=5
            )
            if response.status_code == 400:
                results["passed"] += 1
                self.log("✅ Malicious file type rejected")
            else:
                results["failed"] += 1
                results["errors"].append(f"Malicious file accepted: {response.status_code}")
                self.log(f"❌ Malicious file accepted: {response.status_code}", "ERROR")
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"Malicious file test failed: {e}")
        
        return results
    
    def test_memory_pressure(self) -> Dict[str, Any]:
        """Test application under memory pressure."""
        self.log("Testing memory pressure resilience...")
        results = {"test": "memory_pressure", "passed": 0, "failed": 0, "errors": []}
        
        def memory_stress_request():
            try:
                # Create medium-sized image
                image_data = self.create_test_image(2.0)  # 2MB
                response = requests.post(
                    f"{self.base_url}/upload_photo",
                    files={"file": ("test.jpg", image_data, "image/jpeg")},
                    timeout=10
                )
                return response.status_code
            except:
                return 0
        
        # Concurrent uploads to stress memory
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [
                executor.submit(memory_stress_request)
                for _ in range(50)
            ]
            
            successful = 0
            for future in as_completed(futures, timeout=60):
                try:
                    status = future.result()
                    if status in [200, 400, 413, 429]:  # Any controlled response
                        successful += 1
                except:
                    pass
        
        if successful > 40:  # At least 80% should be handled gracefully
            results["passed"] += 1
            self.log(f"✅ Memory pressure handled: {successful}/50 requests")
        else:
            results["failed"] += 1
            results["errors"].append(f"Poor memory pressure handling: {successful}/50")
            self.log(f"❌ Memory pressure failed: {successful}/50", "ERROR")
        
        return results
    
    def test_concurrent_connections(self) -> Dict[str, Any]:
        """Test concurrent connection handling."""
        self.log("Testing concurrent connection resilience...")
        results = {"test": "concurrent_connections", "passed": 0, "failed": 0, "errors": []}
        
        def concurrent_request(delay: float = 0):
            time.sleep(delay)
            try:
                response = requests.get(f"{self.base_url}/books", timeout=5)
                return response.status_code == 200
            except:
                return False
        
        # Simulate burst of concurrent connections
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [
                executor.submit(concurrent_request, random.uniform(0, 1))
                for _ in range(200)
            ]
            
            successful = sum(1 for future in as_completed(futures, timeout=30) 
                           if future.result())
        
        if successful > 160:  # At least 80% success rate
            results["passed"] += 1
            self.log(f"✅ Concurrent connections handled: {successful}/200")
        else:
            results["failed"] += 1
            results["errors"].append(f"Poor concurrency handling: {successful}/200")
            self.log(f"❌ Concurrency failed: {successful}/200", "ERROR")
        
        return results
    
    def test_security_headers(self) -> Dict[str, Any]:
        """Test security headers presence."""
        self.log("Testing security headers...")
        results = {"test": "security_headers", "passed": 0, "failed": 0, "errors": []}
        
        required_headers = {
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "same-origin"
        }
        
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            
            for header, expected_value in required_headers.items():
                if header in response.headers:
                    if response.headers[header] == expected_value:
                        results["passed"] += 1
                        self.log(f"✅ {header}: {expected_value}")
                    else:
                        results["failed"] += 1
                        results["errors"].append(f"{header} wrong value: {response.headers[header]}")
                        self.log(f"❌ {header} wrong value", "ERROR")
                else:
                    results["failed"] += 1
                    results["errors"].append(f"{header} missing")
                    self.log(f"❌ {header} missing", "ERROR")
                    
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"Headers test failed: {e}")
        
        return results
    
    def test_input_validation_chaos(self) -> Dict[str, Any]:
        """Test input validation with malicious inputs."""
        self.log("Testing input validation...")
        results = {"test": "input_validation", "passed": 0, "failed": 0, "errors": []}
        
        malicious_inputs = [
            {"title": "A" * 10000, "isbn": "1234567890123"},  # Very long title
            {"title": "<script>alert('xss')</script>", "isbn": "1234567890123"},  # XSS
            {"title": "'; DROP TABLE books; --", "isbn": "1234567890123"},  # SQL injection
            {"title": "Normal Book", "isbn": "abc123"},  # Invalid ISBN
            {"title": "Normal Book", "isbn": "12345"},  # Short ISBN
            {"title": "", "isbn": "1234567890123"},  # Empty title
        ]
        
        for payload in malicious_inputs:
            try:
                response = requests.post(
                    f"{self.base_url}/add_manual_title",
                    json=payload,
                    timeout=5
                )
                
                # Should be rejected (400) or handled gracefully
                if response.status_code in [400, 422]:
                    results["passed"] += 1
                    self.log(f"✅ Malicious input rejected: {payload}")
                else:
                    results["failed"] += 1
                    results["errors"].append(f"Malicious input accepted: {payload}")
                    self.log(f"❌ Malicious input accepted: {payload}", "ERROR")
                    
            except Exception as e:
                results["errors"].append(f"Input validation test failed: {e}")
        
        return results
    
    def run_chaos_tests(self) -> Dict[str, Any]:
        """Run all chaos engineering tests."""
        self.log("🔥 Starting Chaos Engineering Tests 🔥")
        
        if not self.start_server():
            return {"error": "Failed to start server"}
        
        try:
            test_methods = [
                self.test_basic_connectivity,
                self.test_security_headers,
                self.test_authentication_bypass_attempts,
                self.test_file_upload_chaos,
                self.test_rate_limiting_chaos,
                self.test_input_validation_chaos,
                self.test_concurrent_connections,
                self.test_memory_pressure,
            ]
            
            all_results = []
            total_passed = 0
            total_failed = 0
            
            for test_method in test_methods:
                try:
                    result = test_method()
                    all_results.append(result)
                    total_passed += result.get("passed", 0)
                    total_failed += result.get("failed", 0)
                    time.sleep(2)  # Cool down between tests
                except Exception as e:
                    self.log(f"Test {test_method.__name__} crashed: {e}", "ERROR")
                    all_results.append({
                        "test": test_method.__name__,
                        "passed": 0,
                        "failed": 1,
                        "errors": [str(e)]
                    })
                    total_failed += 1
            
            # Summary
            self.log("=" * 60)
            self.log("🔥 CHAOS ENGINEERING SUMMARY 🔥")
            self.log("=" * 60)
            
            for result in all_results:
                test_name = result["test"]
                passed = result.get("passed", 0)
                failed = result.get("failed", 0)
                status = "✅ PASS" if failed == 0 else "❌ FAIL"
                self.log(f"{test_name:25} | {status} | {passed}P/{failed}F")
                
                if result.get("errors"):
                    for error in result["errors"][:3]:  # Show first 3 errors
                        self.log(f"  └─ {error}", "ERROR")
            
            self.log("=" * 60)
            success_rate = (total_passed / (total_passed + total_failed)) * 100 if total_passed + total_failed > 0 else 0
            self.log(f"OVERALL: {total_passed} passed, {total_failed} failed ({success_rate:.1f}% success)")
            
            if success_rate >= 80:
                self.log("🎉 APPLICATION PASSED CHAOS TESTS!", "SUCCESS")
            elif success_rate >= 60:
                self.log("⚠️  APPLICATION NEEDS IMPROVEMENT", "WARNING")
            else:
                self.log("💥 APPLICATION FAILED CHAOS TESTS!", "ERROR")
            
            return {
                "summary": {
                    "total_passed": total_passed,
                    "total_failed": total_failed,
                    "success_rate": success_rate,
                    "status": "PASS" if success_rate >= 80 else "FAIL"
                },
                "details": all_results
            }
            
        finally:
            self.stop_server()


def main():
    """Main entry point for chaos testing."""
    try:
        chaos = ChaosEngineer()
        results = chaos.run_chaos_tests()
        
        # Exit with appropriate code
        if results.get("summary", {}).get("status") == "PASS":
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Chaos tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"💥 Chaos testing crashed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 