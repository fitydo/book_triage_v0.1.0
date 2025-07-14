# Scripts

This directory contains utility scripts for testing, deployment, and development operations.

## Testing Scripts

### Unit & Integration Testing
- **`run_tests.py`** - Comprehensive test runner with coverage reporting
- **`test_*.py`** - Individual test modules (moved from root)

### Performance Testing
- **`rps_test.py`** - Simple requests-per-second load testing
- **`comprehensive_rps_test.py`** - Detailed performance analysis with multiple endpoints
- **`performance_test.py`** - Legacy performance testing script

### Security Testing
- **`security_audit.py`** - Security vulnerability scanning and analysis
- **`dast_security_test.py`** - Dynamic Application Security Testing

### Chaos Engineering
- **`chaos_demo.py`** - Demonstration of chaos testing without server requirement
- **`chaos_test.py`** - Full chaos engineering framework with automatic server management
- **`simple_chaos.py`** - Lightweight chaos testing for running servers

## Deployment Scripts

### Windows Deployment
- **`start_book_triage.bat`** - Windows batch script to start the application
- **`start_simple.bat`** - Simple startup script for basic usage
- **`start_book_triage.ps1`** - PowerShell version of the startup script
- **`create_distribution.bat`** - Build distribution packages
- **`create_shortcut.bat`** - Create desktop shortcuts

## Usage Examples

### Run All Tests
```bash
# Comprehensive testing
python scripts/run_tests.py

# Individual test categories
python -m pytest tests/test_api.py -v
python -m pytest tests/test_core.py -v
python -m pytest tests/test_cli.py -v
python -m pytest tests/test_vision.py -v
```

### Performance Testing
```bash
# Quick RPS test
python scripts/rps_test.py

# Comprehensive performance analysis
python scripts/comprehensive_rps_test.py

# Results will show:
# - Requests per second
# - Response times
# - Error rates
# - Performance rating
```

### Security Testing
```bash
# Security audit
python scripts/security_audit.py

# DAST security testing
python scripts/dast_security_test.py

# Results include:
# - Vulnerability assessment
# - Security score
# - Remediation recommendations
```

### Chaos Engineering
```bash
# Demo without server (safe for CI)
python scripts/chaos_demo.py

# Test against running server
python scripts/simple_chaos.py

# Full chaos testing with server management
python scripts/chaos_test.py
```

### Windows Deployment
```batch
REM Start the application
scripts\start_book_triage.bat

REM Create distribution
scripts\create_distribution.bat

REM Create desktop shortcut
scripts\create_shortcut.bat
```

## Script Dependencies

Most scripts require the main application to be installed:
```bash
pip install -e .
```

Additional dependencies for specific scripts:
- **Performance testing**: `requests`, `concurrent.futures`
- **Security testing**: `bandit`, `safety`
- **Chaos testing**: `requests`, `threading`

## Development Workflow

1. **Before commits**: Run `python scripts/run_tests.py`
2. **Before deployment**: Run performance and security tests
3. **After deployment**: Run chaos engineering tests
4. **Regular monitoring**: Use RPS tests for performance baseline

## CI/CD Integration

These scripts are integrated into the GitHub Actions CI pipeline:
- Unit tests run on every push
- Performance tests run on main branch
- Security scans run on pull requests
- Chaos tests validate production readiness

## Environment Variables

Scripts may require these environment variables:
```bash
BOOK_USER=test_user
BOOK_PASS=test_pass
OPENAI_API_KEY=your_key_here  # For vision testing
```

Set these in your environment or create a `.env` file in the project root. 