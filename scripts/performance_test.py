#!/usr/bin/env python3
"""
Performance Testing Script for Book Triage API
Measures RPS (Requests Per Second) and response times for various endpoints.
"""

import asyncio
import time
import statistics
import tempfile
from pathlib import Path
from typing import List, Dict, Any
import threading
import sys

import httpx
import pandas as pd
import uvicorn

from book_triage.api import app, initialize_app


class PerformanceTest:
    """Performance testing suite for Book Triage API."""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.temp_csv = None
        
    def setup_test_data(self):
        """Set up test CSV data with 100 sample books."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.temp_csv = Path(temp_file.name)
        
        # Create test data
        test_data = []
        for i in range(100):
            test_data.append({
                "id": f"perf_test_{i}",
                "title": f"Test Book {i}",
                "url": f"https://amazon.co.jp/book{i}",
                "url_com": f"https://amazon.com/book{i}",
                "purchase_price": 1000 + (i * 10),
                "used_price": 500 + (i * 5),
                "F": (i % 6),
                "R": ((i + 1) % 6),
                "A": ((i + 2) % 6),
                "V": ((i + 3) % 6),
                "S": ((i + 4) % 6),
                "P": ((i + 5) % 6),
                "decision": "unknown",
                "verified": "no",
                "isbn": f"978{i:010d}",
                "citation_R": "[]",
                "citation_P": "[]"
            })
        
        df = pd.DataFrame(test_data)
        df.to_csv(self.temp_csv, index=False)
        temp_file.close()
        
        print(f"Created test CSV with {len(test_data)} records")
        return self.temp_csv
    
    def start_test_server(self):
        """Start the FastAPI server for testing."""
        print("Starting test server on port 8001...")
        
        # Initialize the app with test data
        initialize_app(self.temp_csv, scan_cost=2)
        
        # Start server in a separate thread
        def run_server():
            uvicorn.run(
                app,
                host="127.0.0.1",
                port=8001,
                log_level="error",
                access_log=False
            )
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        for i in range(30):
            try:
                response = httpx.get(f"{self.base_url}/health", timeout=2.0)
                if response.status_code == 200:
                    print(f"Server ready after {i+1} attempts")
                    return True
            except:
                time.sleep(0.5)
        
        raise Exception("Failed to start test server")
    
    async def measure_endpoint(self, method: str, endpoint: str, num_requests: int = 100, concurrent: int = 10, **kwargs) -> Dict[str, Any]:
        """Measure performance of a specific endpoint."""
        
        async def make_request(client: httpx.AsyncClient) -> Dict[str, Any]:
            start_time = time.time()
            try:
                if method.upper() == "GET":
                    response = await client.get(endpoint, **kwargs)
                elif method.upper() == "POST":
                    response = await client.post(endpoint, **kwargs)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                end_time = time.time()
                return {
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                    "success": 200 <= response.status_code < 300
                }
            except Exception as e:
                end_time = time.time()
                return {
                    "status_code": 0,
                    "response_time": end_time - start_time,
                    "success": False,
                    "error": str(e)
                }
        
        # Control concurrency
        semaphore = asyncio.Semaphore(concurrent)
        
        async def limited_request(client):
            async with semaphore:
                return await make_request(client)
        
        start_time = time.time()
        
        async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
            tasks = [limited_request(client) for _ in range(num_requests)]
            results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate statistics
        response_times = [r["response_time"] for r in results]
        success_count = sum(1 for r in results if r["success"])
        
        return {
            "endpoint": endpoint,
            "method": method,
            "total_requests": num_requests,
            "successful_requests": success_count,
            "failed_requests": num_requests - success_count,
            "total_time": total_time,
            "rps": num_requests / total_time if total_time > 0 else 0,
            "avg_response_time": statistics.mean(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "median_response_time": statistics.median(response_times) if response_times else 0,
            "p95_response_time": sorted(response_times)[int(len(response_times) * 0.95)] if response_times else 0,
            "success_rate": (success_count / num_requests) * 100 if num_requests > 0 else 0
        }
    
    async def run_tests(self) -> List[Dict[str, Any]]:
        """Run comprehensive performance tests."""
        
        test_cases = [
            {
                "name": "Health Check",
                "method": "GET",
                "endpoint": "/health",
                "requests": 200,
                "concurrent": 20
            },
            {
                "name": "Root HTML Page",
                "method": "GET", 
                "endpoint": "/",
                "requests": 100,
                "concurrent": 10
            },
            {
                "name": "Get Books List",
                "method": "GET",
                "endpoint": "/books", 
                "requests": 100,
                "concurrent": 10
            },
            {
                "name": "Add Manual Title",
                "method": "POST",
                "endpoint": "/add_manual_title",
                "requests": 50,
                "concurrent": 5,
                "json": {"title": "Performance Test Book", "isbn": "9781234567890"}
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            print(f"\nTesting {test_case['name']}...")
            
            kwargs = {}
            if "json" in test_case:
                kwargs["json"] = test_case["json"]
            
            result = await self.measure_endpoint(
                method=test_case["method"],
                endpoint=test_case["endpoint"],
                num_requests=test_case["requests"],
                concurrent=test_case["concurrent"],
                **kwargs
            )
            
            result["test_name"] = test_case["name"]
            results.append(result)
            
            print(f"  RPS: {result['rps']:.2f}")
            print(f"  Avg Response Time: {result['avg_response_time']*1000:.2f}ms")
            print(f"  Success Rate: {result['success_rate']:.1f}%")
        
        return results
    
    def print_results(self, results: List[Dict[str, Any]]):
        """Print formatted performance test results."""
        
        print("\n" + "="*80)
        print("BOOK TRIAGE API PERFORMANCE TEST RESULTS")
        print("="*80)
        
        # Summary table
        print(f"\n{'Test Name':<25} {'RPS':<10} {'Avg (ms)':<10} {'P95 (ms)':<10} {'Success %':<10}")
        print("-" * 75)
        
        for result in results:
            print(f"{result['test_name']:<25} "
                  f"{result['rps']:<10.2f} "
                  f"{result['avg_response_time']*1000:<10.2f} "
                  f"{result['p95_response_time']*1000:<10.2f} "
                  f"{result['success_rate']:<10.1f}")
        
        # Overall summary
        if results:
            avg_rps = statistics.mean([r['rps'] for r in results])
            avg_response_time = statistics.mean([r['avg_response_time'] for r in results])
            overall_success_rate = statistics.mean([r['success_rate'] for r in results])
            
            print(f"\n{'='*80}")
            print("OVERALL PERFORMANCE SUMMARY")
            print("="*80)
            print(f"Average RPS across all endpoints: {avg_rps:.2f}")
            print(f"Average Response Time: {avg_response_time*1000:.2f}ms")
            print(f"Overall Success Rate: {overall_success_rate:.1f}%")
            
            # Performance assessment
            print(f"\n{'='*40}")
            print("PERFORMANCE ASSESSMENT")
            print("="*40)
            
            if avg_rps > 100:
                print("🚀 Excellent performance - High throughput API")
            elif avg_rps > 50:
                print("✅ Good performance - Production ready")
            elif avg_rps > 20:
                print("⚠️  Moderate performance")
            else:
                print("❌ Poor performance - Needs optimization")
            
            if avg_response_time < 0.1:
                print("🚀 Excellent response times")
            elif avg_response_time < 0.5:
                print("✅ Good response times")
            else:
                print("⚠️  Slow response times")
    
    def cleanup(self):
        """Clean up test resources."""
        if self.temp_csv and self.temp_csv.exists():
            self.temp_csv.unlink()
            print(f"Cleaned up test file")
    
    async def run_performance_tests(self):
        """Run the complete performance test suite."""
        try:
            print("Book Triage API Performance Testing")
            print("="*50)
            
            # Setup
            self.setup_test_data()
            self.start_test_server()
            
            # Wait for server to be ready
            await asyncio.sleep(2)
            
            # Run tests
            results = await self.run_tests()
            
            # Print results
            self.print_results(results)
            
            return results
            
        except Exception as e:
            print(f"Performance test failed: {e}")
            return []
        finally:
            self.cleanup()


async def main():
    """Main function to run performance tests."""
    test_runner = PerformanceTest()
    await test_runner.run_performance_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nPerformance test interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

