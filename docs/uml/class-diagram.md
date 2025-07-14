# Class Diagram - Book Triage System

This class diagram shows the static structure of the Book Triage application, including all major classes, their attributes, methods, and relationships.

```mermaid
classDiagram
    %% Core Business Logic
    class Decision {
        <<enumeration>>
        SELL
        DIGITAL 
        KEEP
        UNKNOWN
    }

    class BookRecord {
        +id: str
        +title: str
        +url: str
        +url_com: str
        +purchase_price: float
        +used_price: float
        +F: Optional[int]
        +R: Optional[int]
        +A: Optional[int]
        +V: Optional[int]
        +S: Optional[int]
        +P: Optional[int]
        +decision: Decision
        +verified: str
        +citation_R: List[str]
        +citation_P: List[str]
        +isbn: str
        +to_dict() Dict[str, Any]
    }

    class BookTriage {
        +csv_path: Path
        +scan_cost: int
        +client: OpenAI
        +records: List[BookRecord]
        +__init__(csv_path, scan_cost)
        +_load_csv() None
        +_save_csv() None
        +calculate_utilities(record) Dict[str, float]
        +make_decision(record) Decision
        +enrich_with_gpt4o(record) None
        +add_record(record) None
        +scan_and_enrich() None
        +get_records() List[BookRecord]
        +get_record_by_id(record_id) Optional[BookRecord]
    }

    %% Vision Processing
    class VisionProcessor {
        +use_openai_vision: bool
        +client: Optional[OpenAI]
        +__init__(use_openai_vision)
        +extract_title_from_image(image_path) str
        +extract_title_and_isbn_from_image(image_path) Tuple[str, str]
        +_extract_with_openai_vision(image_path) str
        +_extract_with_tesseract(image_path) str
        +generate_id() str
    }

    %% API Layer
    class FastAPIApp {
        +title: str
        +version: str
        +book_triage: Optional[BookTriage]
        +vision_processor: Optional[VisionProcessor]
        +initialize_app(csv_path, scan_cost) None
        +root(request) HTMLResponse
        +upload_photo(request, file) Dict[str, Any]
        +get_books(request) List[Dict[str, Any]]
        +scan_books(request, current_user) Dict[str, str]
        +add_manual_title(request) Dict
        +health_check() Dict[str, str]
    }

    class SecurityHeadersMiddleware {
        +dispatch(request, call_next) Response
    }

    %% Security
    class SecurityModule {
        +security: HTTPBasic
        +get_current_user(credentials) str
        +admin_required(func) Callable
        +validate_file_upload(file_content, max_size_mb) None
        +sanitize_image(file_content) bytes
    }

    %% CLI Interface
    class CLIApp {
        +cli: Typer
        +scan(csv, scan_cost, verbose) None
        +web(csv, host, port, scan_cost, reload, verbose) None
        +create_csv(csv, sample) None
        +info(csv) None
    }

    %% External Dependencies
    class OpenAI {
        <<external>>
        +chat: ChatCompletions
        +completions: Completions
    }

    class Tesseract {
        <<external>>
        +image_to_string(image, lang) str
    }

    class FastAPI {
        <<framework>>
        +add_middleware(middleware) None
        +get(path) Decorator
        +post(path) Decorator
    }

    class Typer {
        <<framework>>
        +command() Decorator
        +run() None
    }

    class Pandas {
        <<external>>
        +DataFrame: class
        +read_csv(path) DataFrame
        +to_csv(path) None
    }

    %% Relationships
    BookRecord ||--|| Decision : has
    BookTriage ||--o{ BookRecord : manages
    BookTriage ||--|| OpenAI : uses
    VisionProcessor ||--|| OpenAI : uses
    VisionProcessor ||--|| Tesseract : fallback_to
    
    FastAPIApp ||--|| BookTriage : contains
    FastAPIApp ||--|| VisionProcessor : contains
    FastAPIApp ||--|| SecurityHeadersMiddleware : uses
    FastAPIApp ||--|| SecurityModule : uses
    FastAPIApp ||--|| FastAPI : extends
    
    CLIApp ||--|| BookTriage : creates
    CLIApp ||--|| Typer : uses
    
    BookTriage ||--|| Pandas : uses
    
    %% Composition relationships
    BookTriage *-- BookRecord : contains
    FastAPIApp *-- BookTriage : initializes
    FastAPIApp *-- VisionProcessor : initializes

    %% Notes
    note for BookRecord "Data class representing a book<br/>with all metadata and decision<br/>factors (F,R,A,V,S,P)"
    note for BookTriage "Core business logic class<br/>handling CSV operations,<br/>decision making, and AI enrichment"
    note for VisionProcessor "Handles image processing<br/>with dual approach:<br/>OpenAI Vision API + Tesseract OCR"
    note for FastAPIApp "Web interface providing<br/>REST API endpoints<br/>with security middleware"
```

## Key Relationships

### Composition
- **BookTriage** contains multiple **BookRecord** instances
- **FastAPIApp** initializes and contains **BookTriage** and **VisionProcessor**

### Association  
- **BookRecord** has a **Decision** enum value
- **BookTriage** uses **OpenAI** client for AI enrichment
- **VisionProcessor** uses both **OpenAI** and **Tesseract** for image processing

### Dependency
- **CLIApp** creates **BookTriage** instances
- All components depend on external libraries (**Pandas**, **FastAPI**, **Typer**)

## Design Patterns Implemented

1. **Data Class Pattern**: `BookRecord` with structured data and conversion methods
2. **Facade Pattern**: `BookTriage` provides simplified interface to complex operations
3. **Strategy Pattern**: `VisionProcessor` with multiple extraction strategies
4. **Factory Pattern**: ID generation and record creation
5. **Repository Pattern**: CSV-based persistence in `BookTriage`
6. **Middleware Pattern**: `SecurityHeadersMiddleware` for cross-cutting concerns

## Key Features

- **Type Safety**: Extensive use of type hints and Optional types
- **Error Handling**: Graceful fallbacks and exception management
- **Extensibility**: Plugin-style vision processing with multiple backends
- **Security**: Authentication, input validation, and sanitization
- **Persistence**: CSV-based storage with pandas integration
- **AI Integration**: OpenAI GPT-4o for text extraction and metadata enrichment 