# ADR-003: Authentication Strategy - HTTP Basic Auth

## Status
Accepted

## Context
Book Triage needs authentication to protect administrative endpoints like book scanning and data modification. We need a simple, secure authentication mechanism that works well for a personal application without complex user management requirements.

**Requirements:**
- Protect admin endpoints (/scan, /rescan_title, etc.)
- Simple setup with minimal configuration
- No complex user management system needed
- Environment variable configuration
- Compatible with FastAPI
- Suitable for single-user or small team usage
- No external authentication services

**Alternatives Considered:**
1. **No Authentication**: Leave endpoints open
2. **API Keys**: Simple token-based authentication
3. **HTTP Basic Auth**: Username/password via HTTP headers
4. **JWT Tokens**: JSON Web Tokens with expiration
5. **OAuth2**: Full OAuth2 implementation
6. **Session-based**: Traditional web sessions

## Decision
We will use **HTTP Basic Authentication** for protecting administrative endpoints.

**Rationale:**
- **Simplicity**: Easy to implement and understand
- **Standard Protocol**: RFC 7617 standard, universally supported
- **Environment Variables**: Credentials stored as BOOK_USER/BOOK_PASS
- **FastAPI Integration**: Excellent support via FastAPI security utilities
- **Testing Friendly**: Easy to test with TestClient
- **Browser Support**: Built-in browser authentication dialogs
- **No Sessions**: Stateless authentication suitable for API usage
- **Minimal Dependencies**: No additional authentication libraries required

## Consequences

### Positive
- **Quick Implementation**: Minimal code required for setup
- **Universal Support**: Works with all HTTP clients and browsers
- **Stateless**: No session management or token storage needed
- **Environment Security**: Credentials in environment variables, not code
- **Testing**: Simple to include authentication in tests
- **Debugging**: Easy to test endpoints with curl or browser
- **FastAPI Integration**: Clean dependency injection pattern
- **Performance**: No overhead from token validation or database lookups

### Negative
- **Base64 Encoding**: Credentials encoded but not encrypted (requires HTTPS)
- **Browser Caching**: Browsers cache credentials, no easy logout
- **Limited Features**: No user roles, permissions, or token expiration
- **HTTPS Dependency**: Must use HTTPS in production for security
- **Single User Model**: Not suitable for multi-user applications
- **No Audit Trail**: No logging of authentication events

### Mitigation Strategies
- **HTTPS Enforcement**: Require HTTPS in production environments
- **Strong Credentials**: Use strong, randomly generated passwords
- **Environment Security**: Secure environment variable storage
- **Rate Limiting**: Implement rate limiting to prevent brute force attacks
- **Monitoring**: Log failed authentication attempts
- **Documentation**: Clear documentation about HTTPS requirements

## Implementation Details

### FastAPI Security Setup
```python
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, HTTPException, status
import secrets
import os

security = HTTPBasic()

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(
        credentials.username, os.getenv("BOOK_USER", "")
    )
    correct_password = secrets.compare_digest(
        credentials.password, os.getenv("BOOK_PASS", "")
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
```

### Protected Endpoint Pattern
```python
@app.post("/scan")
async def scan_books(current_user: str = Depends(get_current_user)):
    """Protected endpoint requiring authentication"""
    # Implementation
```

### Environment Configuration
```bash
# .env file
BOOK_USER=admin
BOOK_PASS=secure_random_password_here
```

### Testing Integration
```python
def test_protected_endpoint():
    response = client.post("/scan", auth=("admin", "password"))
    assert response.status_code == 200

def test_unauthorized_access():
    response = client.post("/scan")
    assert response.status_code == 401
```

## Security Considerations

### Production Deployment
- **HTTPS Required**: Credentials transmitted securely
- **Strong Passwords**: Use password generators for BOOK_PASS
- **Environment Security**: Secure storage of environment variables
- **Regular Rotation**: Periodic password changes
- **Access Logging**: Monitor authentication attempts

### Protected Endpoints
- `/scan` - Book scanning and enrichment
- `/rescan_title` - Individual book rescanning
- `/add_manual_title` - Manual book addition
- Future admin endpoints

### Public Endpoints
- `/` - Web interface
- `/health` - Health check
- `/books` - Read-only book listing (with rate limiting)
- `/upload_photo` - File upload (business logic protection)

## Performance Impact
- **Minimal Overhead**: Simple string comparison
- **No Database Calls**: Credentials from environment variables
- **Stateless**: No session storage or cleanup required
- **Caching**: FastAPI dependency caching reduces repeated validations

## Testing Strategy
- **Unit Tests**: Authentication logic validation
- **Integration Tests**: Protected endpoint access
- **Security Tests**: Invalid credential handling
- **Rate Limiting Tests**: Brute force protection

## Future Considerations
If the application grows to support multiple users, consider migration to:
- JWT tokens with user management
- OAuth2 integration
- Role-based access control
- User registration and management system

## Related Decisions
- [ADR-002: FastAPI Framework](002-web-framework-fastapi.md) - Framework integration
- [ADR-004: Security Hardening](004-security-hardening-approach.md) - Overall security approach
- [ADR-009: Rate Limiting](009-rate-limiting-slowapi.md) - Brute force protection 