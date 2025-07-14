# ADR-002: Web Framework Selection - FastAPI

## Status
Accepted

## Context
Book Triage requires a web interface to provide REST API endpoints and a web UI for managing book collections. We need to select a Python web framework that provides modern features, good performance, and ease of development.

**Requirements:**
- REST API with JSON responses
- Automatic API documentation
- Type safety and validation
- High performance for API endpoints
- Easy testing capabilities
- Modern Python features support
- File upload handling
- Static file serving for web UI

**Alternatives Considered:**
1. **Flask**: Lightweight micro-framework
2. **Django**: Full-featured web framework
3. **FastAPI**: Modern async web framework
4. **Quart**: Async version of Flask
5. **Starlette**: ASGI framework (FastAPI is built on this)

## Decision
We will use **FastAPI** as the web framework for Book Triage.

**Rationale:**
- **Automatic Documentation**: Built-in OpenAPI/Swagger documentation generation
- **Type Safety**: Pydantic integration for request/response validation
- **Performance**: High performance with async support
- **Modern Python**: Native support for Python 3.6+ features and type hints
- **Easy Testing**: Excellent testing support with TestClient
- **Dependency Injection**: Clean dependency management system
- **Standards-Based**: Built on OpenAPI, JSON Schema standards
- **File Uploads**: Robust file upload handling
- **Security**: Built-in security utilities
- **Community**: Active development and growing ecosystem

## Consequences

### Positive
- **Developer Experience**: Excellent IDE support with type hints and auto-completion
- **API Documentation**: Automatic interactive documentation at `/docs`
- **Validation**: Automatic request/response validation with clear error messages
- **Performance**: Async capabilities provide excellent performance
- **Testing**: Easy to test with built-in TestClient
- **Security**: Built-in support for authentication, CORS, security headers
- **File Handling**: Robust multipart file upload support
- **Standards Compliance**: OpenAPI standard ensures API interoperability

### Negative
- **Learning Curve**: Developers need to understand async programming concepts
- **Ecosystem Maturity**: Newer framework with fewer third-party packages compared to Flask/Django
- **Memory Usage**: Slightly higher memory usage than micro-frameworks
- **Async Complexity**: Need to be careful with blocking operations in async context

### Mitigation Strategies
- **Training**: Team education on async/await patterns
- **Best Practices**: Establish coding standards for async operations
- **Performance Monitoring**: Monitor memory usage and optimize as needed
- **Gradual Adoption**: Start with simple endpoints and gradually add complexity

## Implementation Details

### Core Features Used
- **Path Operations**: REST endpoints with automatic validation
- **Pydantic Models**: Type-safe request/response models
- **Dependency Injection**: For database connections and authentication
- **File Uploads**: For book cover image processing
- **Static Files**: For serving web interface
- **Middleware**: For CORS, security headers, rate limiting

### API Structure
```python
@app.get("/books")
async def get_books() -> List[BookRecord]:
    """Get all books with automatic JSON serialization"""

@app.post("/upload_photo")
async def upload_photo(file: UploadFile) -> dict:
    """Handle file uploads with validation"""
```

### Testing Integration
```python
def test_api_endpoint():
    client = TestClient(app)
    response = client.get("/books")
    assert response.status_code == 200
```

## Performance Characteristics
- **Throughput**: 150-300+ requests/second achieved in testing
- **Latency**: Low latency for typical operations
- **Memory**: Efficient memory usage with proper async patterns
- **Scalability**: Horizontal scaling capabilities with ASGI servers

## Security Integration
- HTTP Basic Authentication for admin endpoints
- Request size limits for file uploads
- Input validation and sanitization
- Security headers middleware integration

## Related Decisions
- [ADR-003: Authentication Strategy](003-authentication-http-basic.md) - Authentication implementation
- [ADR-004: Security Hardening](004-security-hardening-approach.md) - Security features
- [ADR-008: Vision Processing](008-vision-processing-dual-approach.md) - File upload handling
- [ADR-009: Rate Limiting](009-rate-limiting-slowapi.md) - Performance protection 