# Sequence Diagrams - Book Triage System

This document contains sequence diagrams showing the key interaction flows and processes in the Book Triage application.

## 1. Book Photo Upload and Processing

This sequence shows the complete flow when a user uploads a book photo through the web interface.

```mermaid
sequenceDiagram
    participant User
    participant WebUI
    participant API
    participant Security
    participant Vision
    participant OpenAI
    participant Tesseract
    participant Core
    participant CSV

    User->>WebUI: Upload book photo
    WebUI->>API: POST /upload_photo
    API->>Security: validate_file_upload(file)
    Security->>Security: Check file size & type
    Security->>Security: sanitize_image(file)
    Security-->>API: Validated file bytes
    
    API->>Vision: extract_title_and_isbn_from_image(image)
    
    alt OpenAI Vision Available
        Vision->>OpenAI: Chat completion with image
        OpenAI-->>Vision: Extracted text
        Vision->>Vision: Parse title and ISBN
    else OpenAI Vision Failed
        Vision->>Tesseract: image_to_string(image)
        Tesseract-->>Vision: Raw OCR text
        Vision->>Vision: Extract title and ISBN
    end
    
    Vision-->>API: (title, isbn)
    
    API->>Core: create BookRecord(title, isbn)
    Core->>Core: generate_id()
    Core->>Core: add_record(new_record)
    Core->>CSV: save to CSV file
    CSV-->>Core: Success
    
    Core-->>API: New record created
    API-->>WebUI: JSON response with record
    WebUI-->>User: Success message with book details
```

## 2. Manual Title Addition

This sequence shows the workflow when a user manually adds a book title and ISBN.

```mermaid
sequenceDiagram
    participant User
    participant WebUI
    participant API
    participant Core
    participant OpenAI
    participant CSV

    User->>WebUI: Enter title and ISBN manually
    WebUI->>API: POST /add_manual_title
    API->>Core: create BookRecord(title, isbn)
    Core->>Core: generate_id()
    
    Note over Core, OpenAI: Optional AI enrichment
    Core->>OpenAI: enrich_with_gpt4o(record)
    OpenAI-->>Core: Enhanced metadata (urls)
    
    Core->>Core: add_record(record)
    Core->>CSV: save to CSV file
    CSV-->>Core: Success
    
    Core-->>API: Record created
    API-->>WebUI: JSON response
    WebUI-->>User: Success notification
```

## 3. Decision-Making Workflow

This sequence illustrates the utility-based decision making process for a book.

```mermaid
sequenceDiagram
    participant User
    participant WebUI
    participant API
    participant Core
    participant CSV

    User->>WebUI: Update book factors (F,R,A,V,S,P)
    WebUI->>API: POST /update_book
    API->>Core: get_record_by_id(book_id)
    Core-->>API: BookRecord
    
    API->>Core: update record fields
    Core->>Core: calculate_utilities(record)
    
    Note over Core: Utility Calculations<br/>sell = V - (R + S)<br/>digital = F + P - scan_cost<br/>keep = R + A + S
    
    Core->>Core: make_decision(record)
    Core->>Core: Update record.decision
    Core->>CSV: save updated record
    CSV-->>Core: Success
    
    Core-->>API: Updated record with decision
    API-->>WebUI: JSON response
    WebUI-->>User: Updated decision displayed
```

## 4. AI Enrichment Process

This sequence shows how the system enriches book records with AI-powered metadata.

```mermaid
sequenceDiagram
    participant CLI
    participant Core
    participant OpenAI
    participant CSV

    CLI->>Core: scan_and_enrich()
    Core->>Core: get_records()
    
    loop For each book record
        Core->>OpenAI: enrich_with_gpt4o(record)
        
        Note over OpenAI: GPT-4o analyzes book title<br/>and generates relevant URLs
        
        OpenAI-->>Core: Enhanced metadata (URLs)
        Core->>Core: Update record with URLs
        
        Note over Core: Optional price analysis<br/>if purchase_price and used_price available
        
        Core->>Core: calculate_V_from_prices()
        Core->>Core: make_decision(record)
    end
    
    Core->>CSV: save_csv() all updated records
    CSV-->>Core: Save complete
    Core-->>CLI: Enrichment complete
```

## 5. CLI Batch Processing

This sequence shows the CLI workflow for batch processing books.

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Core
    participant Vision
    participant OpenAI
    participant CSV

    User->>CLI: book-triage scan books.csv
    CLI->>Core: BookTriage(csv_path)
    Core->>CSV: load existing records
    CSV-->>Core: List of BookRecord
    
    CLI->>Core: scan_and_enrich()
    
    loop For each record needing processing
        alt Record has image path
            Core->>Vision: extract_title_from_image()
            Vision-->>Core: Extracted title
        end
        
        Core->>OpenAI: enrich_with_gpt4o(record)
        OpenAI-->>Core: Enhanced metadata
        
        Core->>Core: calculate_utilities(record)
        Core->>Core: make_decision(record)
    end
    
    Core->>CSV: save all updated records
    CSV-->>Core: Save complete
    
    Core-->>CLI: Processing summary
    CLI-->>User: Completion report with statistics
```

## 6. Web Interface Initialization

This sequence shows the startup process for the web interface.

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant API
    participant Core
    participant Vision
    participant CSV

    User->>CLI: book-triage web books.csv
    CLI->>API: initialize_app(csv_path, scan_cost)
    
    API->>Core: BookTriage(csv_path, scan_cost)
    Core->>CSV: load_csv()
    CSV-->>Core: Existing records loaded
    
    API->>Vision: VisionProcessor()
    Vision-->>API: Vision processor ready
    
    API-->>CLI: App initialized
    CLI->>API: uvicorn.run() start server
    
    Note over API: Server listening on host:port
    
    API-->>User: Web interface available
    
    User->>API: GET / (access web interface)
    API-->>User: HTML interface served
```

## 7. Error Handling and Fallback

This sequence demonstrates the error handling and fallback mechanisms.

```mermaid
sequenceDiagram
    participant API
    participant Vision
    participant OpenAI
    participant Tesseract
    participant Core

    API->>Vision: extract_title_from_image(image)
    
    Vision->>OpenAI: Chat completion request
    
    alt OpenAI Success
        OpenAI-->>Vision: Extracted text
    else OpenAI Failure (API limit, network, etc.)
        OpenAI--xVision: Error
        Vision->>Tesseract: image_to_string(image)
        Tesseract-->>Vision: OCR text (fallback)
    end
    
    Vision-->>API: Title extracted (primary or fallback)
    
    API->>Core: enrich_with_gpt4o(record)
    
    alt GPT-4o Enrichment Success
        Core->>OpenAI: Metadata enrichment
        OpenAI-->>Core: Enhanced data
    else GPT-4o Enrichment Failure
        Core-->>Core: Skip enrichment, log warning
    end
    
    Core-->>API: Record processed (with or without enrichment)
```

## Key Interaction Patterns

### 1. **Dual-Path Processing**
- Primary: OpenAI Vision API for high-quality extraction
- Fallback: Tesseract OCR for offline/backup processing

### 2. **Asynchronous Enrichment**
- AI enrichment happens independently of core functionality
- System remains functional even if AI services are unavailable

### 3. **Graceful Degradation**
- Each component has fallback mechanisms
- User experience maintained despite service failures

### 4. **Stateless Operations**
- Web API is stateless with data persistence in CSV
- CLI operations are atomic and can be repeated safely

### 5. **Security Integration**
- Authentication and validation occur early in request flow
- File sanitization prevents security vulnerabilities

These sequence diagrams illustrate the robust, fault-tolerant design of the Book Triage system with clear separation of concerns and multiple fallback strategies. 