# Deployment Diagram - Book Triage System

This deployment diagram illustrates the runtime environment, deployment architecture, and cross-platform considerations for the Book Triage system.

```mermaid
graph TB
    %% User Devices
    subgraph "User Environment"
        Browser[Web Browser<br/>Chrome, Firefox, Safari, Edge]
        Terminal[Terminal/Command Line<br/>cmd, PowerShell, bash, zsh]
    end
    
    %% Local Deployment Node
    subgraph "Local Machine"
        subgraph "Windows 10/11"
            WinPython[Python 3.11+<br/>Windows Distribution]
            WinApp[Book Triage App<br/>Windows Package]
            WinScripts[Startup Scripts<br/>.bat, .ps1]
            WinTesseract[Tesseract OCR<br/>Windows Binary]
        end
        
        subgraph "Linux (Ubuntu/CentOS)"
            LinuxPython[Python 3.11+<br/>System Package]
            LinuxApp[Book Triage App<br/>Linux Distribution]
            LinuxScripts[Startup Scripts<br/>.sh, bash]
            LinuxTesseract[Tesseract OCR<br/>apt/yum package]
        end
        
        subgraph "macOS"
            MacPython[Python 3.11+<br/>Homebrew/System]
            MacApp[Book Triage App<br/>macOS Package]
            MacScripts[Startup Scripts<br/>.sh, zsh]
            MacTesseract[Tesseract OCR<br/>Homebrew package]
        end
    end
    
    %% Application Runtime
    subgraph "Application Runtime"
        subgraph "Web Mode"
            FastAPI[FastAPI Server<br/>uvicorn<br/>Port: 8000]
            WebUI[Web Interface<br/>HTML/CSS/JavaScript]
            Middleware[Security Middleware<br/>Rate Limiting<br/>Authentication]
        end
        
        subgraph "CLI Mode"
            Typer[Typer CLI<br/>Command Processing]
            BatchProcessor[Batch Operations<br/>Scan & Enrich]
        end
        
        subgraph "Core Components"
            BookTriage[BookTriage Core<br/>Business Logic]
            VisionProcessor[Vision Processor<br/>Image Analysis]
            SecurityModule[Security Module<br/>Auth & Validation]
        end
    end
    
    %% Data Storage
    subgraph "Data Layer"
        CSV[CSV Files<br/>books.csv<br/>Persistent Storage]
        TempFiles[Temporary Files<br/>Uploaded Images<br/>Processing Cache]
        Logs[Log Files<br/>Application Logs<br/>Error Tracking]
        Config[Configuration<br/>.env Files<br/>Environment Variables]
    end
    
    %% External Services
    subgraph "Cloud Services"
        OpenAI[OpenAI API<br/>GPT-4o Vision<br/>Text Completion<br/>HTTPS/REST]
    end
    
    %% Network Connections
    Browser --> FastAPI : HTTP/HTTPS
    Terminal --> Typer : Direct Execution
    
    %% Platform-specific connections
    WinApp --> FastAPI
    WinApp --> Typer
    LinuxApp --> FastAPI
    LinuxApp --> Typer
    MacApp --> FastAPI
    MacApp --> Typer
    
    %% Application internal connections
    FastAPI --> Middleware
    FastAPI --> BookTriage
    Typer --> BookTriage
    BookTriage --> VisionProcessor
    BookTriage --> SecurityModule
    
    %% Vision processing connections
    VisionProcessor --> OpenAI : HTTPS API
    VisionProcessor --> WinTesseract : Local Binary
    VisionProcessor --> LinuxTesseract : Local Binary
    VisionProcessor --> MacTesseract : Local Binary
    
    %% Data connections
    BookTriage --> CSV
    VisionProcessor --> TempFiles
    FastAPI --> Logs
    Typer --> Logs
    
    %% Configuration
    WinApp --> Config
    LinuxApp --> Config
    MacApp --> Config
    
    %% Styling
    classDef userDevice fill:#e1f5fe
    classDef platform fill:#f3e5f5
    classDef runtime fill:#e8f5e8
    classDef data fill:#fff3e0
    classDef external fill:#ffebee
    classDef network stroke:#1976d2,stroke-width:2px
    
    class Browser,Terminal userDevice
    class WinPython,WinApp,WinScripts,WinTesseract,LinuxPython,LinuxApp,LinuxScripts,LinuxTesseract,MacPython,MacApp,MacScripts,MacTesseract platform
    class FastAPI,WebUI,Middleware,Typer,BatchProcessor,BookTriage,VisionProcessor,SecurityModule runtime
    class CSV,TempFiles,Logs,Config data
    class OpenAI external
```

## Deployment Architecture Details

### Platform Support Matrix

| Component | Windows | Linux | macOS | Notes |
|-----------|---------|-------|-------|-------|
| **Python Runtime** | 3.11+ | 3.11+ | 3.11+ | Core requirement |
| **Package Manager** | pip | pip/apt | pip/brew | Dependency management |
| **Tesseract OCR** | Binary | Package | Homebrew | Local fallback |
| **Startup Scripts** | .bat/.ps1 | .sh | .sh | Platform-specific |
| **Process Management** | Windows Service | systemd | launchd | Optional |

### Deployment Configurations

#### 1. Development Environment
```
Local Machine
├── Python Virtual Environment
├── Source Code
├── Development Dependencies
├── Test Data (CSV files)
└── Environment Configuration (.env)
```

#### 2. Production Web Server
```
Server Node
├── Python Application Server (uvicorn)
├── Reverse Proxy (nginx/Apache) [Optional]
├── SSL/TLS Certificates
├── Process Manager (systemd/supervisor)
├── Log Rotation
└── Backup System
```

#### 3. Standalone CLI Distribution
```
Distribution Package
├── Python Runtime (bundled)
├── Application Code
├── Dependencies (wheels)
├── Tesseract Binary
├── Startup Scripts
└── Documentation
```

### Network Architecture

#### Web Mode
- **Frontend**: Browser → HTTP/HTTPS → FastAPI Server
- **API**: RESTful endpoints with JSON responses
- **Security**: Basic Auth, HTTPS, Security Headers
- **Rate Limiting**: Per-IP request throttling

#### CLI Mode
- **Direct Execution**: Local binary execution
- **No Network**: Operates offline except for AI features
- **File I/O**: Direct CSV and image file access

### Security Considerations

#### Authentication & Authorization
- **HTTP Basic Auth**: Username/password authentication
- **Environment Variables**: Secure credential storage
- **Session Management**: Stateless API design
- **Input Validation**: File type and size validation

#### Network Security
- **HTTPS Support**: TLS encryption for web interface
- **CORS Headers**: Cross-origin request protection
- **Security Headers**: XSS, clickjacking protection
- **Rate Limiting**: DoS attack prevention

### External Dependencies

#### OpenAI API Integration
- **Connection**: HTTPS REST API
- **Authentication**: API key via environment variable
- **Fallback**: Graceful degradation when unavailable
- **Rate Limits**: Respect OpenAI usage limits

#### Tesseract OCR
- **Installation**: Platform-specific package management
- **Configuration**: Environment variable for binary path
- **Languages**: English + Japanese support
- **Performance**: Local processing, no network required

### Data Management

#### Persistent Storage
- **Format**: CSV files with pandas DataFrame
- **Location**: Configurable file system path
- **Backup**: User-managed file copying
- **Concurrency**: File locking for multi-user access

#### Temporary Storage
- **Images**: Secure temporary file handling
- **Cleanup**: Automatic removal after processing
- **Security**: File sanitization and validation

### Cross-Platform Considerations

#### File System
- **Path Handling**: Platform-agnostic path operations
- **Permissions**: Appropriate file/directory permissions
- **Case Sensitivity**: Cross-platform filename handling

#### Process Management
- **Startup**: Platform-specific launcher scripts
- **Service Installation**: Optional system service integration
- **Process Monitoring**: Health checks and restart capabilities

### Scalability Options

#### Horizontal Scaling
- **Load Balancer**: Multiple FastAPI instances
- **Shared Storage**: Network-attached CSV storage
- **Session Handling**: Stateless design enables scaling

#### Vertical Scaling
- **Memory**: Configurable pandas DataFrame caching
- **CPU**: Parallel processing for batch operations
- **Storage**: SSD recommended for large datasets

### Monitoring & Maintenance

#### Logging
- **Application Logs**: Structured logging with levels
- **Access Logs**: HTTP request/response logging
- **Error Tracking**: Exception capture and reporting

#### Health Monitoring
- **Health Endpoint**: `/health` for service monitoring
- **Dependency Checks**: OpenAI API connectivity
- **Resource Monitoring**: Memory and disk usage

#### Backup & Recovery
- **Data Backup**: Regular CSV file backups
- **Configuration Backup**: Environment variable snapshots
- **Recovery Procedures**: Documented restore processes

This deployment architecture ensures the Book Triage system can operate effectively across different platforms while maintaining security, performance, and reliability requirements. 