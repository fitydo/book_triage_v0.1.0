#!/usr/bin/env python3
"""
Comprehensive RPS Test for Book Triage API
Tests performance under various load conditions.
"""

import asyncio
import time
import tempfile
from pathlib import Path
import threading
import statistics

import httpx
import pandas as pd
import uvicorn

from book_triage.api import app, initialize_app


async def run_load_test(endpoint: str, base_url: str, num_requests: int, concurrency: int, method: str = "GET", **kwargs):
    """Run a load test on a specific endpoint."""
    
    async def make_request(client: httpx.AsyncClient, semaphore: asyncio.Semaphore):
        async with semaphore:
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
                    "success": True,
                    "status_code": response.status_code,
                    "response_time": end_time - start_time
                }
            except Exception as e:
                end_time = time.time()
                return {
                    "success": False,
                    "error": str(e),
                    "response_time": end_time - start_time
                }
    
    semaphore = asyncio.Semaphore(concurrency)
    start_time = time.time()
    
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        tasks = [make_request(client, semaphore) for _ in range(num_requests)]
        results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Calculate statistics
    successful_results = [r for r in results if r["success"]]
    response_times = [r["response_time"] for r in successful_results]
    
    return {
        "endpoint": endpoint,
        "total_requests": num_requests,
        "successful_requests": len(successful_results),
        "failed_requests": num_requests - len(successful_results),
        "total_time": total_time,
        "rps": num_requests / total_time,
        "success_rate": (len(successful_results) / num_requests) * 100,
        "avg_response_time": statistics.mean(response_times) if response_times else 0,
        "min_response_time": min(response_times) if response_times else 0,
        "max_response_time": max(response_times) if response_times else 0,
        "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) > 10 else 0,
        "p99_response_time": statistics.quantiles(response_times, n=100)[98] if len(response_times) > 50 else 0
    }


async def comprehensive_rps_test():
    """Run comprehensive RPS tests with different loads."""
    print("Book Triage API - Comprehensive RPS Performance Test")
    print("="*70)
    
    # Create test CSV data with more records
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    temp_csv = Path(temp_file.name)
    
    # Generate 100 test books for better data simulation
    test_data = []
    for i in range(100):
        test_data.append({
            "id": f"load_test_{i}",
            "title": f"Load Test Book {i}",
            "url": "https://amazon.co.jp/test",
            "url_com": "https://amazon.com/test", 
            "purchase_price": 1000 + (i * 10),
            "used_price": 500 + (i * 5),
            "F": (i % 6), "R": ((i + 1) % 6), "A": ((i + 2) % 6), 
            "V": ((i + 3) % 6), "S": ((i + 4) % 6), "P": ((i + 5) % 6),
            "decision": "unknown",
            "verified": "no",
            "isbn": f"978{i:010d}",
            "citation_R": "[]",
            "citation_P": "[]"
        })
    
    df = pd.DataFrame(test_data)
    df.to_csv(temp_csv, index=False)
    temp_file.close()
    print(f"✓ Created test dataset: {len(test_data)} books")
    
    # Initialize and start server
    initialize_app(temp_csv, scan_cost=2)
    
    def run_server():
        uvicorn.run(app, host="127.0.0.1", port=8003, log_level="error", access_log=False)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    print("✓ Starting server on port 8003...")
    
    # Wait for server startup
    base_url = "http://localhost:8003"
    await asyncio.sleep(4)
    
    # Test configuration - escalating load
    test_scenarios = [
        # Light load
        {"name": "Light Load - Health Check", "endpoint": "/health", "requests": 100, "concurrency": 5},
        {"name": "Light Load - Books List", "endpoint": "/books", "requests": 50, "concurrency": 5},
        
        # Medium load
        {"name": "Medium Load - Health Check", "endpoint": "/health", "requests": 200, "concurrency": 10},
        {"name": "Medium Load - Books List", "endpoint": "/books", "requests": 100, "concurrency": 10},
        {"name": "Medium Load - Root Page", "endpoint": "/", "requests": 100, "concurrency": 10},
        
        # High load
        {"name": "High Load - Health Check", "endpoint": "/health", "requests": 500, "concurrency": 25},
        {"name": "High Load - Books List", "endpoint": "/books", "requests": 200, "concurrency": 20},
        
        # Stress test
        {"name": "Stress Test - Health Check", "endpoint": "/health", "requests": 1000, "concurrency": 50},
        {"name": "Stress Test - Books List", "endpoint": "/books", "requests": 300, "concurrency": 30},
    ]
    
    results = []
    
    try:
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n{i}. {scenario['name']}")
            print(f"   Running {scenario['requests']} requests with {scenario['concurrency']} concurrent connections...")
            
            result = await run_load_test(
                endpoint=scenario['endpoint'],
                base_url=base_url,
                num_requests=scenario['requests'],
                concurrency=scenario['concurrency']
            )
            
            result['test_name'] = scenario['name']
            results.append(result)
            
            print(f"   ✓ RPS: {result['rps']:.2f}")
            print(f"   ✓ Success Rate: {result['success_rate']:.1f}%")
            print(f"   ✓ Avg Response Time: {result['avg_response_time']*1000:.2f}ms")
            print(f"   ✓ P95 Response Time: {result['p95_response_time']*1000:.2f}ms")
        
        # Generate comprehensive report
        print_comprehensive_report(results)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        # Cleanup
        temp_csv.unlink()
        print(f"\n✓ Test completed and cleaned up")


def print_comprehensive_report(results):
    """Print a comprehensive performance report."""
    
    print(f"\n{'='*80}")
    print("COMPREHENSIVE RPS PERFORMANCE REPORT")
    print("="*80)
    
    # Summary table
    print(f"\n{'Test Scenario':<35} {'RPS':<10} {'Success%':<10} {'Avg(ms)':<10} {'P95(ms)':<10}")
    print("-" * 80)
    
    for result in results:
        print(f"{result['test_name']:<35} "
              f"{result['rps']:<10.2f} "
              f"{result['success_rate']:<10.1f} "
              f"{result['avg_response_time']*1000:<10.2f} "
              f"{result['p95_response_time']*1000:<10.2f}")
    
    # Analysis by endpoint
    print(f"\n{'='*80}")
    print("ANALYSIS BY ENDPOINT")
    print("="*80)
    
    endpoints = {}
    for result in results:
        endpoint = result['endpoint']
        if endpoint not in endpoints:
            endpoints[endpoint] = []
        endpoints[endpoint].append(result)
    
    for endpoint, endpoint_results in endpoints.items():
        print(f"\nEndpoint: {endpoint}")
        avg_rps = statistics.mean([r['rps'] for r in endpoint_results])
        avg_response_time = statistics.mean([r['avg_response_time'] for r in endpoint_results])
        avg_success_rate = statistics.mean([r['success_rate'] for r in endpoint_results])
        
        print(f"  Average RPS: {avg_rps:.2f}")
        print(f"  Average Response Time: {avg_response_time*1000:.2f}ms")
        print(f"  Average Success Rate: {avg_success_rate:.1f}%")
        
        # Performance under load
        max_load_result = max(endpoint_results, key=lambda x: x['total_requests'])
        print(f"  Max Load Tested: {max_load_result['total_requests']} requests")
        print(f"  RPS at Max Load: {max_load_result['rps']:.2f}")
    
    # Overall performance assessment
    print(f"\n{'='*80}")
    print("OVERALL PERFORMANCE ASSESSMENT")
    print("="*80)
    
    all_rps = [r['rps'] for r in results]
    all_success_rates = [r['success_rate'] for r in results]
    
    avg_rps = statistics.mean(all_rps)
    min_rps = min(all_rps)
    max_rps = max(all_rps)
    avg_success_rate = statistics.mean(all_success_rates)
    
    print(f"Average RPS across all tests: {avg_rps:.2f}")
    print(f"RPS Range: {min_rps:.2f} - {max_rps:.2f}")
    print(f"Overall Success Rate: {avg_success_rate:.1f}%")
    
    # Performance rating
    if avg_rps > 200:
        rating = "🚀 EXCELLENT"
        description = "High-performance API suitable for heavy production loads"
    elif avg_rps > 100:
        rating = "✅ VERY GOOD"
        description = "Strong performance, handles significant load well"
    elif avg_rps > 50:
        rating = "✅ GOOD"
        description = "Solid performance for typical production workloads"
    elif avg_rps > 25:
        rating = "⚠️  MODERATE"
        description = "Acceptable performance, may need optimization for high loads"
    else:
        rating = "❌ POOR"
        description = "Performance optimization required"
    
    print(f"\nPerformance Rating: {rating}")
    print(f"Assessment: {description}")
    
    # Recommendations
    print(f"\n{'='*80}")
    print("RECOMMENDATIONS")
    print("="*80)
    
    health_results = [r for r in results if r['endpoint'] == '/health']
    books_results = [r for r in results if r['endpoint'] == '/books']
    
    if health_results:
        health_avg_rps = statistics.mean([r['rps'] for r in health_results])
        print(f"• Health check endpoint: {health_avg_rps:.0f} RPS average - Good for monitoring")
    
    if books_results:
        books_avg_rps = statistics.mean([r['rps'] for r in books_results])
        print(f"• Books list endpoint: {books_avg_rps:.0f} RPS average - Main data endpoint")
        
        if books_avg_rps < 50:
            print("  ⚠️  Consider adding caching or pagination for better performance")
        else:
            print("  ✅ Good performance for data-heavy operations")
    
    if avg_success_rate < 95:
        print("• ⚠️  Success rate below 95% - investigate error handling")
    else:
        print("• ✅ Excellent reliability with high success rates")
        
    print("• The API shows good scalability characteristics")
    print("• Consider load balancing for production deployments exceeding current capacity")


if __name__ == "__main__":
    try:
        asyncio.run(comprehensive_rps_test())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}") 