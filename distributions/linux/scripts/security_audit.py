#!/usr/bin/env python3
"""
Security Audit Script for Book Triage Application
Performs comprehensive security analysis and vulnerability testing.
"""

import asyncio
import tempfile
import json
import os
import time
from pathlib import Path
from typing import Dict, Any, List
import threading

import httpx
import pandas as pd
import uvicorn

from book_triage.api import app, initialize_app


class SecurityAuditor:
    """Comprehensive security auditing for Book Triage API."""
    
    def __init__(self, base_url: str = "http://localhost:8004"):
        self.base_url = base_url
        self.temp_csv = None
        self.vulnerabilities = []
        self.security_score = 100
        
    def setup_test_server(self):
        """Set up test server with sample data."""
        print("Setting up test server for security audit...")
        
        # Create test CSV
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.temp_csv = Path(temp_file.name)
        
        test_data = [{
            "id": "security_test_1",
            "title": "Security Test Book",
            "url": "https://amazon.co.jp/test",
            "url_com": "https://amazon.com/test",
            "purchase_price": 1000,
            "used_price": 500,
            "F": 3, "R": 2, "A": 1, "V": 4, "S": 2, "P": 3,
            "decision": "unknown",
            "verified": "no",
            "isbn": "9781234567890",
            "citation_R": "[]",
            "citation_P": "[]"
        }]
        
        df = pd.DataFrame(test_data)
        df.to_csv(self.temp_csv, index=False)
        temp_file.close()
        
        # Initialize and start server
        initialize_app(self.temp_csv, scan_cost=2)
        
        def run_server():
            uvicorn.run(app, host="127.0.0.1", port=8004, log_level="error", access_log=False)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for server
        time.sleep(3)
        print("✓ Test server started on port 8004")
    
    def add_vulnerability(self, severity: str, category: str, description: str, recommendation: str):
        """Add a vulnerability to the findings."""
        score_impact = {"critical": 30, "high": 20, "medium": 10, "low": 5}
        self.security_score -= score_impact.get(severity.lower(), 0)
        
        self.vulnerabilities.append({
            "severity": severity,
            "category": category,
            "description": description,
            "recommendation": recommendation
        })
    
    async def test_input_validation(self):
        """Test input validation and sanitization."""
        print("\n🔍 Testing Input Validation...")
        
        # Test malicious file uploads
        print("  • Testing file upload security...")
        
        # Test non-image file upload
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
                malicious_content = b"#!/bin/bash\necho 'malicious script'"
                files = {"file": ("script.sh", malicious_content, "application/x-sh")}
                response = await client.post("/upload_photo", files=files)
                
                if response.status_code != 400:
                    self.add_vulnerability(
                        "HIGH", "Input Validation",
                        "Application accepts non-image files in photo upload",
                        "Implement strict file type validation based on file content, not just MIME type"
                    )
                else:
                    print("    ✓ Non-image files properly rejected")
        except Exception as e:
            print(f"    ⚠️  Upload test failed: {e}")
        
        # Test JSON injection in manual title endpoint
        print("  • Testing JSON injection...")
        
        injection_payloads = [
            {"title": "<script>alert('XSS')</script>", "isbn": "1234567890123"},
            {"title": "'; DROP TABLE books; --", "isbn": "1234567890123"},
            {"title": "Test", "isbn": "' OR '1'='1"},
            {"title": "A" * 1000, "isbn": "1234567890123"},  # Large input
        ]
        
        for payload in injection_payloads:
            try:
                async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
                    response = await client.post("/add_manual_title", json=payload)
                    
                    if response.status_code == 200:
                        # Check if dangerous content was processed
                        data = response.json()
                        if "<script>" in str(data) or "DROP TABLE" in str(data):
                            self.add_vulnerability(
                                "HIGH", "Input Validation",
                                f"Potential injection vulnerability with payload: {payload}",
                                "Implement input sanitization and output encoding"
                            )
            except Exception as e:
                pass  # Expected for malformed requests
        
        print("    ✓ JSON injection tests completed")
    
    async def test_authentication_authorization(self):
        """Test authentication and authorization mechanisms."""
        print("\n🔐 Testing Authentication & Authorization...")
        
        # Check if any endpoints require authentication
        endpoints = ["/", "/books", "/health", "/scan"]
        
        unauthenticated_access = []
        for endpoint in endpoints:
            try:
                async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
                    response = await client.get(endpoint)
                    if response.status_code == 200:
                        unauthenticated_access.append(endpoint)
            except:
                pass
        
        if unauthenticated_access:
            self.add_vulnerability(
                "MEDIUM", "Authentication",
                f"Endpoints accessible without authentication: {unauthenticated_access}",
                "Consider implementing authentication for administrative endpoints like /scan"
            )
            print(f"    ⚠️  Unauthenticated access to: {unauthenticated_access}")
        else:
            print("    ✓ All endpoints require authentication")
    
    async def test_dos_vulnerabilities(self):
        """Test for Denial of Service vulnerabilities."""
        print("\n💥 Testing DoS Vulnerabilities...")
        
        # Test rate limiting
        print("  • Testing rate limiting...")
        
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
                tasks = [client.get("/health") for _ in range(50)]
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                successful = sum(1 for r in responses if not isinstance(r, Exception) and hasattr(r, 'status_code') and r.status_code == 200)
                
                if successful >= 45:  # Most requests succeeded
                    self.add_vulnerability(
                        "MEDIUM", "DoS Protection",
                        "No rate limiting detected - all requests succeeded",
                        "Implement rate limiting to prevent abuse"
                    )
                    print(f"    ⚠️  No rate limiting: {successful}/50 requests succeeded")
                else:
                    print(f"    ✓ Rate limiting detected: {successful}/50 requests succeeded")
        except Exception as e:
            print(f"    ⚠️  Rate limiting test failed: {e}")
    
    async def test_data_validation(self):
        """Test data validation and sanitization."""
        print("\n✅ Testing Data Validation...")
        
        # Test ISBN validation
        print("  • Testing ISBN validation...")
        
        invalid_isbns = [
            "123",  # Too short
            "12345678901234",  # Too long
            "123456789012a",  # Contains letter
            "",  # Empty
        ]
        
        for isbn in invalid_isbns:
            try:
                async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
                    response = await client.post("/add_manual_title", json={"title": "Test", "isbn": isbn})
                    
                    if response.status_code == 200:
                        self.add_vulnerability(
                            "LOW", "Data Validation",
                            f"Invalid ISBN accepted: {isbn}",
                            "Strengthen ISBN validation"
                        )
            except:
                pass
        
        print("    ✓ Data validation tests completed")
    
    async def test_security_headers(self):
        """Test security headers."""
        print("\n🛡️  Testing Security Headers...")
        
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
                response = await client.get("/")
                headers = response.headers
                
                security_headers = [
                    "X-Content-Type-Options",
                    "X-Frame-Options", 
                    "X-XSS-Protection",
                    "Content-Security-Policy"
                ]
                
                missing_headers = [h for h in security_headers if h not in headers]
                
                if missing_headers:
                    self.add_vulnerability(
                        "MEDIUM", "Security Headers",
                        f"Missing security headers: {', '.join(missing_headers)}",
                        "Implement security headers to prevent XSS, clickjacking, and other attacks"
                    )
                    print(f"    ⚠️  Missing headers: {missing_headers}")
                else:
                    print("    ✓ All security headers present")
        except Exception as e:
            print(f"    ⚠️  Security headers test failed: {e}")
    
    def check_static_security(self):
        """Check static security issues in the codebase."""
        print("\n📁 Checking Static Security Issues...")
        
        # Check for secure OpenAI API key usage
        env_example = Path("book_triage/env_example.txt")
        if env_example.exists():
            content = env_example.read_text()
            if "your_openai_api_key_here" in content:
                print("    ✓ OpenAI API key properly configured via environment")
            else:
                self.add_vulnerability(
                    "MEDIUM", "Secret Management",
                    "OpenAI API key configuration unclear",
                    "Ensure API keys are loaded from environment variables"
                )
        
        print("    ✓ Static security analysis completed")
    
    def generate_report(self):
        """Generate comprehensive security report."""
        print(f"\n{'='*80}")
        print("🔒 SECURITY AUDIT REPORT")
        print("="*80)
        
        # Overall score
        print(f"\nSecurity Score: {self.security_score}/100")
        
        if self.security_score >= 90:
            rating = "🟢 EXCELLENT"
        elif self.security_score >= 70:
            rating = "🟡 GOOD"
        elif self.security_score >= 50:
            rating = "🟠 MODERATE" 
        else:
            rating = "🔴 POOR"
        
        print(f"Security Rating: {rating}")
        
        # Vulnerability summary
        if not self.vulnerabilities:
            print("\n✅ No critical security vulnerabilities found!")
        else:
            print(f"\n📋 Found {len(self.vulnerabilities)} security issues:")
            
            severity_counts = {}
            for vuln in self.vulnerabilities:
                severity = vuln["severity"]
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            for severity, count in severity_counts.items():
                print(f"  • {severity}: {count}")
            
            print(f"\n{'='*80}")
            print("DETAILED VULNERABILITY REPORT")
            print("="*80)
            
            for i, vuln in enumerate(self.vulnerabilities, 1):
                print(f"\n{i}. {vuln['severity']} - {vuln['category']}")
                print(f"   Description: {vuln['description']}")
                print(f"   Recommendation: {vuln['recommendation']}")
        
        # Security recommendations
        print(f"\n{'='*80}")
        print("SECURITY RECOMMENDATIONS")
        print("="*80)
        
        recommendations = [
            "🔐 Implement authentication for administrative endpoints",
            "🛡️  Add security headers (HSTS, CSP, X-Frame-Options)",
            "📊 Implement rate limiting to prevent abuse",
            "🔍 Add comprehensive input validation",
            "📁 Implement file size limits for uploads",
            "🌐 Use HTTPS in production",
            "🔑 Rotate API keys regularly",
            "📝 Implement logging and monitoring",
            "🧪 Regular security testing"
        ]
        
        for rec in recommendations:
            print(f"  {rec}")
    
    def cleanup(self):
        """Clean up test resources."""
        if self.temp_csv and self.temp_csv.exists():
            self.temp_csv.unlink()
    
    async def run_security_audit(self):
        """Run complete security audit."""
        try:
            print("🔒 Book Triage Security Audit")
            print("="*50)
            
            self.setup_test_server()
            
            # Run all security tests
            await self.test_input_validation()
            await self.test_authentication_authorization()
            await self.test_dos_vulnerabilities()
            await self.test_data_validation()
            await self.test_security_headers()
            self.check_static_security()
            
            # Generate report
            self.generate_report()
            
        except Exception as e:
            print(f"❌ Security audit failed: {e}")
        finally:
            self.cleanup()


async def main():
    """Main function for security audit."""
    auditor = SecurityAuditor()
    await auditor.run_security_audit()


if __name__ == "__main__":
    asyncio.run(main())
