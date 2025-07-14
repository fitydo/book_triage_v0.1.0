# Book Triage Security Checklist

## 🚨 Critical (Fix Before Production)

### [ ] 1. Implement HTTPS
```bash
# For production deployment
# Use proper TLS certificates
# Redirect HTTP to HTTPS
```

### [ ] 2. Add Authentication
```python
# Add to book_triage/api.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    is_correct_username = secrets.compare_digest(credentials.username, "admin")
    is_correct_password = secrets.compare_digest(credentials.password, "your_secure_password")
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Protect admin endpoints
@app.post("/scan")
async def scan_books(user: str = Depends(get_current_user)):
    # existing code...
```

### [ ] 3. Add Security Headers
```python
# Add to book_triage/api.py
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'"
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

### [ ] 4. Add Rate Limiting
```bash
pip install slowapi
```

```python
# Add to book_triage/api.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/upload_photo")
@limiter.limit("10/minute")
async def upload_photo(request: Request, file: UploadFile = File(...)):
    # existing code...

@app.post("/scan")
@limiter.limit("5/hour")
async def scan_books(request: Request, user: str = Depends(get_current_user)):
    # existing code...
```

## ⚠️ High Priority (Next Sprint)

### [ ] 5. Enhance File Upload Security
```python
# Add to book_triage/api.py
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@app.post("/upload_photo")
@limiter.limit("10/minute")
async def upload_photo(request: Request, file: UploadFile = File(...)):
    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    
    # Validate file signature
    if not (content.startswith(b'\xff\xd8\xff') or  # JPEG
            content.startswith(b'\x89PNG') or        # PNG
            content.startswith(b'GIF87a') or         # GIF87a
            content.startswith(b'GIF89a')):          # GIF89a
        raise HTTPException(status_code=400, detail="Invalid image format")
    
    # existing validation code...
```

### [ ] 6. Improve Input Validation
```bash
pip install bleach
```

```python
import bleach
from typing import Optional

def sanitize_input(text: str, max_length: int = 500) -> str:
    """Sanitize user input."""
    if len(text) > max_length:
        raise HTTPException(status_code=400, detail=f"Input too long (max {max_length} characters)")
    return bleach.clean(text, tags=[], strip=True)

@app.post("/add_manual_title")
async def add_manual_title(request: Request):
    data = await request.json()
    title = sanitize_input(data.get("title", "").strip())
    isbn = data.get("isbn", "").strip()
    # existing validation...
```

### [ ] 7. Add Logging and Monitoring
```python
import logging
from datetime import datetime

# Configure security logging
security_logger = logging.getLogger("security")
handler = logging.FileHandler("security.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
security_logger.addHandler(handler)
security_logger.setLevel(logging.INFO)

@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    
    # Log security-relevant events
    if request.url.path in ["/scan", "/upload_photo", "/add_manual_title"]:
        security_logger.info(f"Access to {request.url.path} from {request.client.host}")
    
    return response
```

## 📋 Medium Priority

### [ ] 8. Environment Configuration
```bash
# Create .env file (don't commit to git)
OPENAI_API_KEY=your_actual_api_key_here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password_here
SECRET_KEY=your_secret_key_here
```

### [ ] 9. Secure CSV File Access
```python
import os
from pathlib import Path

def secure_csv_path(csv_path: str) -> Path:
    """Ensure CSV path is secure."""
    path = Path(csv_path).resolve()
    
    # Ensure it's within allowed directory
    allowed_dir = Path.cwd() / "data"
    if not str(path).startswith(str(allowed_dir)):
        raise ValueError("CSV path not allowed")
    
    return path
```

### [ ] 10. Add Request Validation
```python
from pydantic import BaseModel, validator

class BookInput(BaseModel):
    title: str
    isbn: str
    
    @validator('title')
    def validate_title(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Title is required')
        if len(v) > 500:
            raise ValueError('Title too long')
        return v.strip()
    
    @validator('isbn')
    def validate_isbn(cls, v):
        if not v.isdigit() or len(v) != 13:
            raise ValueError('ISBN must be exactly 13 digits')
        return v

@app.post("/add_manual_title")
async def add_manual_title(book_input: BookInput, user: str = Depends(get_current_user)):
    # Use validated input
    title = book_input.title
    isbn = book_input.isbn
    # existing code...
```

## 🔍 Low Priority (Future)

### [ ] 11. Advanced Authentication
- Consider JWT tokens for API access
- Implement user roles and permissions
- Add session management

### [ ] 12. Database Migration
- Move from CSV to proper database
- Implement proper data encryption
- Add database connection security

### [ ] 13. Security Testing Automation
```bash
# Add to CI/CD pipeline
pip install bandit safety
bandit -r book_triage/
safety check
```

### [ ] 14. Production Deployment Security
```yaml
# docker-compose.yml example
version: '3.8'
services:
  book-triage:
    build: .
    ports:
      - "443:8000"
    environment:
      - HTTPS_ONLY=true
    volumes:
      - ./data:/app/data:ro
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    user: "1000:1000"
```

## Security Testing Checklist

### [ ] Manual Testing
- [ ] Try accessing admin endpoints without authentication
- [ ] Test file upload with non-image files
- [ ] Test with very large files
- [ ] Test with malicious filenames
- [ ] Test XSS payloads in form inputs
- [ ] Test SQL injection patterns (even though using CSV)

### [ ] Automated Testing
```python
# Add to tests/test_security.py
def test_authentication_required():
    """Test that admin endpoints require authentication."""
    response = client.post("/scan")
    assert response.status_code == 401

def test_file_upload_validation():
    """Test file upload security."""
    files = {"file": ("test.txt", b"not an image", "text/plain")}
    response = client.post("/upload_photo", files=files)
    assert response.status_code == 400

def test_rate_limiting():
    """Test rate limiting works."""
    for _ in range(20):
        response = client.get("/health")
    # Should eventually get rate limited
```

## Dependency Security

### [ ] Regular Updates
```bash
# Check for security updates
pip list --outdated
pip-audit  # Install: pip install pip-audit
```

### [ ] Current Dependencies Status
- ✅ FastAPI 0.115.14 (Latest, no known vulnerabilities)
- ✅ OpenAI 1.93.0 (Latest, no known vulnerabilities)  
- ✅ Pandas 2.3.0 (Recent, no known vulnerabilities)
- ✅ Uvicorn 0.35.0 (Latest, no known vulnerabilities)

## Monitoring & Alerting

### [ ] Security Monitoring
- [ ] Set up log monitoring for failed authentication attempts
- [ ] Monitor for unusual API usage patterns
- [ ] Alert on file upload anomalies
- [ ] Track rate limiting violations

### [ ] Health Checks
- [ ] Add security-specific health checks
- [ ] Monitor certificate expiration
- [ ] Check for configuration drift

---

## Implementation Order

1. **Week 1**: Items 1-4 (Critical security basics)
2. **Week 2**: Items 5-7 (Enhanced security)
3. **Week 3**: Items 8-10 (Production hardening)
4. **Ongoing**: Security testing and monitoring

Remember: Security is not a one-time task. Regular reviews and updates are essential! 