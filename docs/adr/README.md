# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records for the Book Triage project. ADRs document the architectural decisions that have been made during the development of this project.

## ADR Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-001](001-data-storage-csv.md) | Data Storage Using CSV Files | Accepted | 2024-01-01 |
| [ADR-002](002-web-framework-fastapi.md) | Web Framework Selection - FastAPI | Accepted | 2024-01-01 |
| [ADR-003](003-authentication-http-basic.md) | Authentication Strategy - HTTP Basic Auth | Accepted | 2024-01-01 |
| [ADR-004](004-security-hardening-approach.md) | Security Hardening Implementation | Accepted | 2024-01-01 |
| [ADR-005](005-testing-strategy-comprehensive.md) | Comprehensive Testing Strategy | Accepted | 2024-01-01 |
| [ADR-006](006-cross-platform-distribution.md) | Cross-Platform Distribution Strategy | Accepted | 2024-01-01 |
| [ADR-007](007-ci-cd-github-actions.md) | CI/CD Pipeline with GitHub Actions | Accepted | 2024-01-01 |
| [ADR-008](008-vision-processing-dual-approach.md) | Vision Processing - Dual OCR Approach | Accepted | 2024-01-01 |
| [ADR-009](009-rate-limiting-slowapi.md) | Rate Limiting Implementation | Accepted | 2024-01-01 |
| [ADR-010](010-project-structure-modular.md) | Modular Project Structure | Accepted | 2024-01-01 |

## ADR Format

We follow the standard ADR format:

- **Title**: A short, descriptive title
- **Status**: Proposed, Accepted, Deprecated, Superseded
- **Context**: The situation that motivates this decision
- **Decision**: The architectural decision and its rationale
- **Consequences**: The positive and negative consequences of this decision

## How to Contribute

When making significant architectural decisions:
1. Create a new ADR using the next sequential number
2. Follow the established format
3. Update this index
4. Get the ADR reviewed before implementation 