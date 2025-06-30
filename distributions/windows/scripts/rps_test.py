#!/usr/bin/env python3
"""
Simple RPS Test for Book Triage API
"""

import asyncio
import time
import tempfile
from pathlib import Path
import threading

import httpx
import pandas as pd
import uvicorn

from book_triage.api import app, initialize_app


async def test_rps():
    """Test RPS performance of Book Triage API."""
    print("Book Triage API - RPS Performance Test")
    print("="*50)
    
    # Create test CSV data
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    temp_csv = Path(temp_file.name)
    
    # Generate 50 test books
    test_data = []
    for i in range(50):
        test_data.append({
            "id": f"test_{i}",
            "title": f"Test Book {i}",
            "url": "https://amazon.co.jp/test",
            "url_com": "https://amazon.com/test", 
            "purchase_price": 1000,
            "used_price": 500,
            "F": 3, "R": 2, "A": 1, "V": 4, "S": 2, "P": 3,
            "decision": "unknown",
            "verified": "no",
            "isbn": f"978{i:010d}",
            "citation_R": "[]",
            "citation_P": "[]"
        })
    
    df = pd.DataFrame(test_data)
    df.to_csv(temp_csv, index=False)
    temp_file.close()
    print(f"Created test data: {len(test_data)} books")
    
    # Initialize and start server
    initialize_app(temp_csv, scan_cost=2)
    
    def run_server():
        uvicorn.run(app, host="127.0.0.1", port=8002, log_level="error", access_log=False)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    print("Starting server on port 8002...")
    
    # Wait for server startup
    base_url = "http://localhost:8002"
    await asyncio.sleep(3)
    
    try:
        # Test 1: Health Check Endpoint
        print("\n1. Testing /health endpoint (100 requests)...")
        start_time = time.time()
        
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            tasks = [client.get("/health") for _ in range(100)]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        successful = sum(1 for r in responses if not isinstance(r, Exception) and hasattr(r, 'status_code') and r.status_code == 200)
        health_rps = 100 / total_time
        
        print(f"   ✓ Successful requests: {successful}/100")
        print(f"   ✓ Total time: {total_time:.3f}s")
        print(f"   ✓ RPS: {health_rps:.2f}")
        
        # Test 2: Books List Endpoint
        print("\n2. Testing /books endpoint (50 requests)...")
        start_time = time.time()
        
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            tasks = [client.get("/books") for _ in range(50)]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        successful = sum(1 for r in responses if not isinstance(r, Exception) and hasattr(r, 'status_code') and r.status_code == 200)
        books_rps = 50 / total_time
        
        print(f"   ✓ Successful requests: {successful}/50")
        print(f"   ✓ Total time: {total_time:.3f}s")
        print(f"   ✓ RPS: {books_rps:.2f}")
        
        # Test 3: Root HTML Page
        print("\n3. Testing / (root) endpoint (30 requests)...")
        start_time = time.time()
        
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            tasks = [client.get("/") for _ in range(30)]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        successful = sum(1 for r in responses if not isinstance(r, Exception) and hasattr(r, 'status_code') and r.status_code == 200)
        root_rps = 30 / total_time
        
        print(f"   ✓ Successful requests: {successful}/30")
        print(f"   ✓ Total time: {total_time:.3f}s")
        print(f"   ✓ RPS: {root_rps:.2f}")
        
        # Summary
        print(f"\n{'='*60}")
        print("RPS PERFORMANCE SUMMARY")
        print("="*60)
        print(f"Health Check RPS:     {health_rps:.2f}")
        print(f"Books List RPS:       {books_rps:.2f}")
        print(f"Root Page RPS:        {root_rps:.2f}")
        
        avg_rps = (health_rps + books_rps + root_rps) / 3
        print(f"Average RPS:          {avg_rps:.2f}")
        
        # Performance Assessment
        print(f"\n{'='*60}")
        print("PERFORMANCE ASSESSMENT")
        print("="*60)
        
        if avg_rps > 100:
            print("🚀 EXCELLENT - High performance API (>100 RPS)")
        elif avg_rps > 50:
            print("✅ GOOD - Solid performance for production (>50 RPS)")
        elif avg_rps > 25:
            print("⚠️  MODERATE - Acceptable performance (>25 RPS)")
        else:
            print("❌ POOR - May need optimization (<25 RPS)")
        
        print(f"\nThe Book Triage API can handle {avg_rps:.0f} requests per second on average.")
        
        if health_rps > books_rps * 2:
            print("Note: Simple endpoints (health) perform much better than data endpoints.")
        
        return {
            "health_rps": health_rps,
            "books_rps": books_rps,
            "root_rps": root_rps,
            "average_rps": avg_rps
        }
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None
    finally:
        # Cleanup
        temp_csv.unlink()
        print(f"\n✓ Test completed and cleaned up")


if __name__ == "__main__":
    try:
        asyncio.run(test_rps())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}") 