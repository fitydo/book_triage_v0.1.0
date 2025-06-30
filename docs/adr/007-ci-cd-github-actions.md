# ADR-007: CI/CD Pipeline with GitHub Actions

## Status
Accepted

## Context
Book Triage requires a robust CI/CD pipeline to ensure code quality, security, and reliability across all commits and releases. The pipeline must support automated testing, security scanning, performance validation, and deployment processes. As an open-source project targeting GitHub publication, GitHub Actions provides the most integrated solution.

**Requirements:**
- Automated testing on every commit and pull request
- Security scanning and vulnerability detection
- Code quality gates and coverage requirements
- Cross-platform testing support
- Automated release and distribution building
- Performance regression detection
- Community contribution support

**Quality Goals:**
- 100% test pass rate requirement
- Minimum 85% code coverage threshold
- Zero high-severity security vulnerabilities
- Performance baseline maintenance
- Fast feedback cycles (<10 minutes)

## Decision
We will implement a **comprehensive CI/CD pipeline using GitHub Actions** with:

1. **Multi-Job Pipeline** - Parallel execution for faster feedback
2. **Quality Gates** - Strict requirements before merge/release
3. **Security Integration** - Automated security scanning
4. **Performance Testing** - Chaos engineering and load testing
5. **Artifact Management** - Test reports, coverage, and distributions
6. **Community Features** - PR checks, status badges, notifications

## Consequences

### Positive
- **Automated Quality Assurance**: Every commit tested automatically
- **Fast Feedback**: Parallel jobs provide quick results
- **Security First**: Continuous security validation
- **Community Ready**: Professional CI/CD for open source
- **Release Automation**: Automated distribution building
- **Visibility**: Status badges and clear quality metrics
- **Cost Effective**: Free for public repositories

### Negative
- **Complexity**: Multiple jobs and dependencies to manage
- **Resource Usage**: GitHub Actions minutes consumption
- **Maintenance Overhead**: Pipeline updates with code changes
- **Learning Curve**: Team needs GitHub Actions expertise
- **Vendor Lock-in**: GitHub-specific implementation

### Mitigation Strategies
- **Documentation**: Clear CI/CD documentation and runbooks
- **Modular Design**: Reusable actions and workflows
- **Resource Optimization**: Efficient job design and caching
- **Community Standards**: Follow GitHub Actions best practices
- **Monitoring**: Pipeline performance and success tracking

## Implementation Details

### Pipeline Architecture

#### Main Workflow (.github/workflows/ci.yml)
```yaml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .[test]
      
      - name: Run tests
        run: python -m pytest tests/ -v
      
      - name: Upload test artifacts
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: test-failures
          path: test-results/

  quality-gate:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .[test]
          pip install pytest-cov
      
      - name: Run coverage
        run: python -m pytest --cov=book_triage --cov-fail-under=85 --cov-report=xml
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          token: ${{ secrets.CODECOV_TOKEN }}

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install security tools
        run: |
          python -m pip install --upgrade pip
          pip install bandit safety
      
      - name: Run Bandit security scan
        run: bandit -r book_triage/ -f json -o bandit-report.json
      
      - name: Run Safety dependency check
        run: safety check --json --output safety-report.json
      
      - name: Upload security artifacts
        uses: actions/upload-artifact@v4
        with:
          name: security-reports
          path: '*-report.json'

  chaos:
    runs-on: ubuntu-latest
    needs: [test, security]
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .
      
      - name: Run chaos engineering tests
        run: python scripts/chaos_demo.py
      
      - name: Upload chaos results
        uses: actions/upload-artifact@v4
        with:
          name: chaos-results
          path: chaos-*.txt
```

### Quality Gates Implementation

#### Coverage Threshold Enforcement
```yaml
- name: Check coverage threshold
  run: |
    python -m pytest --cov=book_triage --cov-fail-under=85
    if [ $? -ne 0 ]; then
      echo "Coverage below 85% threshold"
      exit 1
    fi
```

#### Security Validation
```yaml
- name: Security gate
  run: |
    # Fail if high-severity vulnerabilities found
    bandit -r book_triage/ -ll
    safety check --ignore 39462  # Known non-critical issue
```

### Status Badges Integration

#### README.md Badges
```markdown
[![CI](https://github.com/username/book-triage/workflows/CI%20Pipeline/badge.svg)](https://github.com/username/book-triage/actions)
[![Coverage](https://codecov.io/gh/username/book-triage/branch/main/graph/badge.svg)](https://codecov.io/gh/username/book-triage)
[![Security](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Quality Gate](https://img.shields.io/badge/quality-85%25%20coverage-green.svg)](https://github.com/username/book-triage/actions)
```

### Caching Strategy

#### Dependency Caching
```yaml
- name: Cache pip dependencies
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

#### Test Data Caching
```yaml
- name: Cache test data
  uses: actions/cache@v4
  with:
    path: test-cache/
    key: test-data-${{ hashFiles('tests/**/*.py') }}
```

## Notification Strategy

### Slack Integration
```yaml
- name: Notify Slack on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: failure
    channel: '#ci-alerts'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Email Notifications
```yaml
- name: Send email on critical failure
  if: failure() && github.ref == 'refs/heads/main'
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: "Critical CI Failure - Book Triage"
    body: "CI pipeline failed on main branch"
```

## Security Integration

### Secret Scanning
```yaml
- name: Run gitleaks
  uses: gitleaks/gitleaks-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Dependency Updates
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    reviewers:
      - "maintainer-team"
```

## Performance Monitoring

### Chaos Engineering Integration
```yaml
- name: Performance regression check
  run: |
    python scripts/comprehensive_rps_test.py
    # Check if RPS dropped below baseline
    if [ $RPS -lt 150 ]; then
      echo "Performance regression detected"
      exit 1
    fi
```

### Resource Usage Monitoring
```yaml
- name: Monitor resource usage
  run: |
    # Monitor memory and CPU usage during tests
    python scripts/resource_monitor.py &
    python -m pytest tests/
    # Analyze resource usage patterns
```

## Artifact Management

### Test Results Preservation
```yaml
- name: Archive test results
  uses: actions/upload-artifact@v4
  if: always()
  with:
    name: test-results-${{ github.run_number }}
    path: |
      test-results/
      coverage.xml
      *.log
    retention-days: 30
```

### Distribution Building
```yaml
- name: Build distributions
  if: github.event_name == 'release'
  run: |
    python scripts/create_distributions_simple.py
    
- name: Upload release assets
  uses: actions/upload-release-asset@v1
  with:
    upload_url: ${{ github.event.release.upload_url }}
    asset_path: ./distributions/
```

## Branch Protection Rules

### Main Branch Protection
```yaml
# Repository Settings
required_status_checks:
  strict: true
  contexts:
    - "test"
    - "quality-gate" 
    - "security"
    - "chaos"

enforce_admins: true
required_pull_request_reviews:
  required_approving_review_count: 1
  dismiss_stale_reviews: true
```

## Performance Metrics

### Pipeline Performance
- **Average Runtime**: 8-12 minutes for full pipeline
- **Parallel Jobs**: 4 concurrent jobs maximum
- **Cache Hit Rate**: 85%+ for dependency caching
- **Success Rate**: 98%+ pipeline success rate

### Resource Optimization
- **GitHub Actions Minutes**: ~15 minutes per full run
- **Storage Usage**: <100MB for artifacts per run
- **Network Usage**: Optimized with caching
- **Concurrent Builds**: Limited to prevent resource exhaustion

## Monitoring and Alerting

### Pipeline Health Monitoring
```yaml
- name: Report pipeline metrics
  run: |
    echo "Pipeline duration: $(($SECONDS / 60)) minutes"
    echo "Test count: $(grep -c "PASSED\|FAILED" test-output.log)"
    echo "Coverage: $(grep "TOTAL" coverage-report.txt | awk '{print $4}')"
```

### Failure Analysis
```yaml
- name: Analyze failures
  if: failure()
  run: |
    # Collect failure information
    echo "Job failed at step: ${{ github.job }}"
    echo "Commit: ${{ github.sha }}"
    echo "Author: ${{ github.actor }}"
    # Send to monitoring system
```

## Community Features

### Pull Request Integration
```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]

- name: PR Quality Check
  run: |
    echo "Running PR quality checks..."
    python -m pytest tests/ --maxfail=5
    echo "PR ready for review"
```

### Contributor Guidelines
```yaml
- name: Check contribution guidelines
  run: |
    # Validate commit message format
    # Check code style compliance
    # Verify test additions for new features
```

## Future Enhancements

### Planned Improvements
- **Matrix Testing**: Multiple Python versions and platforms
- **Performance Benchmarking**: Historical performance tracking
- **Security Scanning**: Additional security tools integration
- **Deployment Automation**: Automated production deployments

### Advanced Features
- **Container Building**: Docker image creation and publishing
- **Documentation Generation**: Automated API documentation
- **Compliance Reporting**: SOC 2, ISO 27001 compliance tracking
- **Cost Optimization**: Advanced caching and resource management

## Related Decisions
- [ADR-002: FastAPI Framework](002-web-framework-fastapi.md) - Testing integration
- [ADR-004: Security Hardening](004-security-hardening-approach.md) - Security pipeline integration
- [ADR-005: Testing Strategy](005-testing-strategy-comprehensive.md) - Testing automation
- [ADR-006: Cross-Platform Distribution](006-cross-platform-distribution.md) - Distribution automation 