# ADR-009: Rate Limiting Implementation

## Status
Accepted

## Context
Book Triage web application needs protection against abuse, DoS attacks, and resource exhaustion. Without rate limiting, malicious users could overwhelm the server with requests, affecting performance for legitimate users. The application serves both public endpoints (like health checks) and resource-intensive operations (like book scanning and AI processing) that require different protection levels.

**Security Requirements:**
- Prevent DoS attacks and resource exhaustion
- Protect expensive operations (AI API calls, file processing)
- Allow reasonable usage for legitimate users
- Maintain good performance under normal load
- Provide clear feedback when limits are exceeded

**Operational Requirements:**
- Different limits for different endpoint types
- Exemptions for monitoring endpoints
- Easy configuration and tuning
- Integration with existing FastAPI infrastructure
- Performance monitoring and alerting

## Decision
We will implement **comprehensive rate limiting using SlowAPI** with:

1. **Tiered Rate Limiting** - Different limits based on endpoint resource usage
2. **IP-Based Limiting** - Per-client IP address rate limiting
3. **Endpoint-Specific Rules** - Customized limits for different operations
4. **Health Check Exemptions** - Monitoring endpoints excluded from limits
5. **Graceful Error Handling** - Clear HTTP 429 responses with retry information

## Consequences

### Positive
- **DoS Protection**: Prevents overwhelming the server with requests
- **Resource Conservation**: Protects expensive operations (AI, file processing)
- **Fair Usage**: Ensures reasonable access for all users
- **Performance Stability**: Maintains response times under load
- **Security Hardening**: Prevents brute force and abuse attacks
- **Monitoring Integration**: Clear metrics for usage patterns

### Negative
- **User Experience Impact**: Legitimate users may hit limits during peak usage
- **Implementation Complexity**: Additional middleware and configuration
- **Memory Overhead**: Rate limiting state tracking per IP
- **Configuration Management**: Need to tune limits based on usage patterns
- **False Positives**: Shared IP addresses may cause issues

### Mitigation Strategies
- **Generous Limits**: Set reasonable limits that accommodate normal usage
- **Clear Error Messages**: Provide helpful 429 responses with retry guidance
- **Monitoring**: Track limit hits and adjust thresholds as needed
- **Exemption Mechanisms**: Health checks and monitoring excluded
- **Documentation**: Clear API usage guidelines for developers

## Implementation Details

### SlowAPI Integration

#### Core Rate Limiter Setup
```python
# book_triage/api.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

#### Tiered Rate Limiting Strategy
```python
# Different limits for different endpoint categories

# Default rate limit for most endpoints
DEFAULT_LIMIT = "60/minute"

# Stricter limits for resource-intensive operations
BOOKS_ENDPOINT_LIMIT = "30/minute"  # Reading book data
UPLOAD_LIMIT = "10/minute"          # File uploads
SCAN_LIMIT = "5/minute"             # AI-powered scanning

# Health check - no limit for monitoring
HEALTH_EXEMPT = True
```

### Endpoint-Specific Implementation

#### Resource-Intensive Endpoints
```python
@app.get("/books")
@limiter.limit("30/minute")
async def get_books(request: Request):
    """Get books with stricter rate limiting"""
    # Implementation with 30 requests per minute limit
    pass

@app.post("/upload_photo")
@limiter.limit("10/minute")
async def upload_photo(request: Request, file: UploadFile):
    """Upload photo with upload-specific limits"""
    # Implementation with 10 uploads per minute limit
    pass

@app.post("/scan")
@limiter.limit("5/minute")
async def scan_books(request: Request, current_user: str = Depends(get_current_user)):
    """Scan books with very strict limits (AI operations)"""
    # Implementation with 5 scans per minute limit
    pass
```

#### Standard Endpoints
```python
@app.get("/")
@limiter.limit("60/minute")
async def root(request: Request):
    """Root endpoint with standard rate limiting"""
    pass

@app.post("/add_manual_title")
@limiter.limit("60/minute")
async def add_manual_title(request: Request, current_user: str = Depends(get_current_user)):
    """Manual title addition with standard limits"""
    pass
```

#### Exempted Endpoints
```python
@app.get("/health")
async def health_check():
    """Health check - no rate limiting for monitoring"""
    # No @limiter.limit decorator - exempt from rate limiting
    return {"status": "healthy"}
```

### Custom Rate Limit Handler

#### Enhanced Error Response
```python
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit exceeded handler"""
    
    response = JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": f"Too many requests. Limit: {exc.detail}",
            "retry_after": exc.retry_after,
            "endpoint": str(request.url),
            "timestamp": datetime.utcnow().isoformat()
        },
        headers={
            "Retry-After": str(exc.retry_after),
            "X-RateLimit-Limit": str(exc.detail),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(int(time.time()) + exc.retry_after)
        }
    )
    
    return response

# Register custom handler
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
```

### Configuration Management

#### Environment-Based Configuration
```python
import os

# Rate limiting configuration from environment variables
RATE_LIMIT_CONFIG = {
    "default": os.getenv("RATE_LIMIT_DEFAULT", "60/minute"),
    "books": os.getenv("RATE_LIMIT_BOOKS", "30/minute"),
    "upload": os.getenv("RATE_LIMIT_UPLOAD", "10/minute"),
    "scan": os.getenv("RATE_LIMIT_SCAN", "5/minute"),
    "storage_uri": os.getenv("RATE_LIMIT_STORAGE", "memory://"),
}

# Dynamic limiter configuration
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=RATE_LIMIT_CONFIG["storage_uri"]
)
```

#### Flexible Limit Assignment
```python
def get_rate_limit_for_endpoint(endpoint_name: str) -> str:
    """Get rate limit for specific endpoint"""
    
    limits = {
        "books": RATE_LIMIT_CONFIG["books"],
        "upload": RATE_LIMIT_CONFIG["upload"],
        "scan": RATE_LIMIT_CONFIG["scan"],
        "health": None,  # No limit
    }
    
    return limits.get(endpoint_name, RATE_LIMIT_CONFIG["default"])

# Usage in decorators
@app.get("/books")
@limiter.limit(get_rate_limit_for_endpoint("books"))
async def get_books(request: Request):
    pass
```

## Advanced Features

### IP Whitelist for Monitoring
```python
MONITORING_IPS = {
    "127.0.0.1",      # Localhost
    "::1",            # IPv6 localhost
    # Add monitoring service IPs
}

def get_rate_limit_key(request: Request):
    """Custom key function with monitoring IP exemption"""
    
    client_ip = get_remote_address(request)
    
    # Exempt monitoring IPs from rate limiting
    if client_ip in MONITORING_IPS:
        return f"monitoring_{client_ip}"
    
    return client_ip

# Use custom key function
limiter = Limiter(key_func=get_rate_limit_key)
```

### Rate Limit Headers
```python
from slowapi.middleware import SlowAPIMiddleware

# Add middleware to include rate limit headers in all responses
app.add_middleware(SlowAPIMiddleware)

# Headers added automatically:
# X-RateLimit-Limit: 60
# X-RateLimit-Remaining: 59
# X-RateLimit-Reset: 1640995200
```

### Burst Handling
```python
# Configure burst allowance for short-term spikes
@app.get("/books")
@limiter.limit("30/minute; 10/second")  # 30 per minute, burst of 10 per second
async def get_books(request: Request):
    """Books endpoint with burst handling"""
    pass
```

## Testing Strategy

### Rate Limiting Tests
```python
# tests/test_api.py
class TestRateLimiting:
    def test_books_endpoint_rate_limit(self, client):
        """Test rate limiting on /books endpoint"""
        
        # Make requests up to the limit
        for i in range(30):
            response = client.get("/books")
            assert response.status_code == 200
        
        # Next request should be rate limited
        response = client.get("/books")
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["error"]
    
    def test_health_endpoint_no_limit(self, client):
        """Test that health endpoint is not rate limited"""
        
        # Make many requests to health endpoint
        for i in range(100):
            response = client.get("/health")
            assert response.status_code == 200
    
    def test_rate_limit_headers(self, client):
        """Test rate limit headers in responses"""
        
        response = client.get("/books")
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
    
    def test_429_response_format(self, client):
        """Test 429 error response format"""
        
        # Exhaust rate limit
        for i in range(31):
            client.get("/books")
        
        response = client.get("/books")
        assert response.status_code == 429
        
        data = response.json()
        assert "error" in data
        assert "retry_after" in data
        assert "Retry-After" in response.headers
```

### Load Testing Integration
```python
# scripts/test_rate_limiting.py
import asyncio
import aiohttp

async def test_rate_limit_enforcement():
    """Test rate limiting under concurrent load"""
    
    async with aiohttp.ClientSession() as session:
        # Send concurrent requests
        tasks = []
        for i in range(100):
            task = session.get("http://localhost:8000/books")
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successful vs rate-limited responses
        success_count = sum(1 for r in responses if r.status == 200)
        rate_limited_count = sum(1 for r in responses if r.status == 429)
        
        print(f"Successful: {success_count}, Rate Limited: {rate_limited_count}")
        
        # Verify rate limiting is working
        assert rate_limited_count > 0
        assert success_count <= 30  # Should not exceed per-minute limit
```

## Monitoring and Observability

### Rate Limiting Metrics
```python
# Metrics collection for rate limiting
class RateLimitMetrics:
    def __init__(self):
        self.total_requests = 0
        self.rate_limited_requests = 0
        self.endpoint_metrics = {}
    
    def record_request(self, endpoint: str, was_rate_limited: bool):
        self.total_requests += 1
        if was_rate_limited:
            self.rate_limited_requests += 1
        
        if endpoint not in self.endpoint_metrics:
            self.endpoint_metrics[endpoint] = {"total": 0, "limited": 0}
        
        self.endpoint_metrics[endpoint]["total"] += 1
        if was_rate_limited:
            self.endpoint_metrics[endpoint]["limited"] += 1
    
    def get_rate_limit_percentage(self):
        if self.total_requests == 0:
            return 0
        return (self.rate_limited_requests / self.total_requests) * 100
```

### Alerting Thresholds
```python
# Alert when rate limiting exceeds thresholds
def check_rate_limiting_health():
    """Check if rate limiting indicates potential issues"""
    
    metrics = get_current_metrics()
    rate_limit_percentage = metrics.get_rate_limit_percentage()
    
    # Alert if too many requests are being rate limited
    if rate_limit_percentage > 10:  # More than 10% rate limited
        send_alert(
            "High rate limiting detected",
            f"Rate limit percentage: {rate_limit_percentage}%"
        )
    
    # Alert if specific endpoints are heavily rate limited
    for endpoint, stats in metrics.endpoint_metrics.items():
        endpoint_percentage = (stats["limited"] / stats["total"]) * 100
        if endpoint_percentage > 20:  # More than 20% for specific endpoint
            send_alert(
                f"High rate limiting on {endpoint}",
                f"Rate limit percentage: {endpoint_percentage}%"
            )
```

## Performance Considerations

### Memory Usage Optimization
```python
# Optimize rate limiter storage for memory efficiency
from slowapi.util import get_remote_address
import time

class OptimizedRateLimiter:
    def __init__(self, max_entries=10000):
        self.storage = {}
        self.max_entries = max_entries
        self.last_cleanup = time.time()
    
    def cleanup_expired_entries(self):
        """Remove expired entries to prevent memory growth"""
        
        current_time = time.time()
        if current_time - self.last_cleanup < 300:  # Cleanup every 5 minutes
            return
        
        expired_keys = []
        for key, data in self.storage.items():
            if data.get("expires", 0) < current_time:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.storage[key]
        
        self.last_cleanup = current_time
```

### Redis Backend for Scaling
```python
# Optional Redis backend for distributed rate limiting
import redis

# Configuration for Redis-based rate limiting
if os.getenv("REDIS_URL"):
    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri=os.getenv("REDIS_URL")
    )
else:
    # Fallback to in-memory storage
    limiter = Limiter(key_func=get_remote_address)
```

## Documentation and User Communication

### API Documentation
```python
# Clear documentation of rate limits in OpenAPI
@app.get("/books", 
    summary="Get all books",
    description="Returns list of all books. Rate limited to 30 requests per minute.",
    responses={
        200: {"description": "List of books"},
        429: {"description": "Rate limit exceeded. Retry after specified time."}
    }
)
@limiter.limit("30/minute")
async def get_books(request: Request):
    pass
```

### User-Friendly Error Messages
```python
# Provide helpful error messages
RATE_LIMIT_MESSAGES = {
    "books": "Too many requests to view books. Please wait before trying again.",
    "upload": "Upload limit reached. Please wait before uploading more files.",
    "scan": "Scan limit reached. AI processing is resource-intensive, please wait.",
    "default": "Request limit exceeded. Please slow down your requests."
}

def get_user_friendly_message(endpoint: str) -> str:
    return RATE_LIMIT_MESSAGES.get(endpoint, RATE_LIMIT_MESSAGES["default"])
```

## Related Decisions
- [ADR-002: FastAPI Framework](002-web-framework-fastapi.md) - Rate limiting middleware integration
- [ADR-003: HTTP Basic Auth](003-authentication-http-basic.md) - Authentication bypass protection
- [ADR-004: Security Hardening](004-security-hardening-approach.md) - DoS protection as part of security
- [ADR-005: Testing Strategy](005-testing-strategy-comprehensive.md) - Rate limiting testing approach 