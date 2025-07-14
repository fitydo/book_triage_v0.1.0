# UML Diagrams for Book Triage

This directory contains comprehensive UML diagrams documenting the Book Triage application architecture and design.

## Overview

The Book Triage application is a decision-making tool that helps users determine whether to sell, digitize, or keep their books based on various utility factors. The system provides both web and CLI interfaces with AI-powered book analysis capabilities.

## Diagram Types

### 1. Class Diagram (`class-diagram.md`)
Shows the static structure of the system including:
- Core business entities (`BookRecord`, `BookTriage`)
- Vision processing components (`VisionProcessor`)
- Security components
- Enums and data structures

### 2. Component Diagram (`component-diagram.md`)
Illustrates the high-level system architecture:
- Module boundaries and dependencies
- External service integrations (OpenAI, Tesseract)
- Data flow between components

### 3. Sequence Diagrams (`sequence-diagrams.md`)
Documents key interaction flows:
- Book photo upload and processing
- Manual title addition
- Decision-making workflow
- AI enrichment process

### 4. Use Case Diagram (`use-case-diagram.md`)
Captures system functionality from user perspective:
- Actor roles (User, Admin)
- Core use cases and their relationships
- System boundaries

### 5. Deployment Diagram (`deployment-diagram.md`)
Shows the runtime environment:
- Application deployment units
- External service dependencies
- Cross-platform considerations

### 6. Activity Diagrams (`activity-diagrams.md`)
Models business processes:
- Book triage decision workflow
- Vision processing pipeline
- Data enrichment process

## Architecture Principles

The Book Triage system follows several key architectural principles:

1. **Modular Design**: Clear separation of concerns across modules
2. **API-First**: FastAPI provides standardized web interface
3. **Dual Interface**: Both web UI and CLI for different use cases
4. **AI Integration**: Leverages OpenAI GPT-4o for text extraction and enrichment
5. **Fallback Processing**: Tesseract OCR as backup for image processing
6. **Security-First**: Authentication, rate limiting, and input validation
7. **Cross-Platform**: Designed to run on Windows, macOS, and Linux

## Key Design Patterns

- **Strategy Pattern**: Vision processing with OpenAI and Tesseract options
- **Factory Pattern**: Record creation and ID generation
- **Repository Pattern**: CSV-based data persistence
- **Facade Pattern**: BookTriage class encapsulates complex operations
- **Middleware Pattern**: Security headers and rate limiting

## Data Flow

1. **Input**: Book photos or manual titles
2. **Processing**: Vision analysis and text extraction
3. **Enrichment**: AI-powered metadata enhancement
4. **Analysis**: Utility-based decision algorithms
5. **Storage**: CSV persistence with data integrity
6. **Output**: Recommendations and detailed reports

## Usage

Each diagram file contains Mermaid syntax that can be rendered in:
- GitHub (native Mermaid support)
- VS Code (with Mermaid extension)
- Online Mermaid editors
- Documentation platforms supporting Mermaid

## Maintenance

These diagrams should be updated when:
- New classes or modules are added
- Significant architectural changes occur
- New integrations are implemented
- Business logic flows change

For questions about the architecture or diagrams, refer to the ADR (Architecture Decision Records) in the `docs/adr/` directory. 