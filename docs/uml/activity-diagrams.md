# Activity Diagrams - Book Triage System

This document contains activity diagrams that model the key business processes and workflows in the Book Triage application.

## 1. Book Triage Decision Workflow

This activity diagram shows the complete decision-making process for determining what to do with a book.

```mermaid
flowchart TD
    Start([Start: Book Needs Decision]) --> HasBook{Book Record<br/>Exists?}
    
    HasBook -->|No| AddBook[Add Book Record]
    HasBook -->|Yes| CheckFactors{All Decision<br/>Factors Available?}
    
    AddBook --> GetTitle[Get Book Title]
    GetTitle --> PhotoOption{Add via Photo<br/>or Manual?}
    
    PhotoOption -->|Photo| UploadPhoto[Upload Book Photo]
    PhotoOption -->|Manual| ManualEntry[Enter Title & ISBN]
    
    UploadPhoto --> ExtractText[Extract Text from Image]
    ExtractText --> VisionSuccess{Text Extraction<br/>Successful?}
    
    VisionSuccess -->|Yes| CreateRecord[Create Book Record]
    VisionSuccess -->|No| ManualEntry
    
    ManualEntry --> CreateRecord
    CreateRecord --> EnrichMetadata[Enrich with AI Metadata]
    
    EnrichMetadata --> CheckFactors
    
    CheckFactors -->|No| CollectFactors[Collect Missing Factors]
    CheckFactors -->|Yes| CalculateUtilities[Calculate Utility Scores]
    
    CollectFactors --> GetF[Get Frequency Score<br/>F: 0-5]
    GetF --> GetR[Get Rarity Score<br/>R: 0-5]
    GetR --> GetA[Get Annotation Need<br/>A: 0-5]
    GetA --> GetV[Get Resale Value<br/>V: 0-5]
    GetV --> GetS[Get Sentimental Value<br/>S: 0-5]
    GetS --> GetP[Get Scannability<br/>P: 0-5]
    GetP --> CalculateUtilities
    
    CalculateUtilities --> SellUtility[Sell Utility = V - R + S]
    SellUtility --> DigitalUtility[Digital Utility = F + P - scan_cost]
    DigitalUtility --> KeepUtility[Keep Utility = R + A + S]
    
    KeepUtility --> CompareUtilities{Which Utility<br/>is Highest?}
    
    CompareUtilities -->|Sell| SellDecision[Decision: SELL<br/>Monetize the book]
    CompareUtilities -->|Digital| DigitalDecision[Decision: DIGITAL<br/>Scan and digitize]
    CompareUtilities -->|Keep| KeepDecision[Decision: KEEP<br/>Retain physical copy]
    CompareUtilities -->|Tie/Negative| UnknownDecision[Decision: UNKNOWN<br/>Needs manual review]
    
    SellDecision --> SaveDecision[Save Decision to CSV]
    DigitalDecision --> SaveDecision
    KeepDecision --> SaveDecision
    UnknownDecision --> SaveDecision
    
    SaveDecision --> NotifyUser[Notify User of Decision]
    NotifyUser --> End([End: Decision Complete])
```

## 2. Vision Processing Pipeline

This activity diagram details the image processing workflow for extracting book information from photos.

```mermaid
flowchart TD
    Start([Start: Image Upload]) --> ValidateImage[Validate Image File]
    ValidateImage --> SizeCheck{File Size<br/>< 10MB?}
    
    SizeCheck -->|No| SizeError[Error: File Too Large]
    SizeCheck -->|Yes| TypeCheck{Valid Image<br/>Format?}
    
    TypeCheck -->|No| FormatError[Error: Invalid Format]
    TypeCheck -->|Yes| SanitizeImage[Sanitize Image<br/>Strip Metadata]
    
    SanitizeImage --> SaveTemp[Save to Temporary File]
    SaveTemp --> VisionStrategy{OpenAI Vision<br/>Available?}
    
    VisionStrategy -->|Yes| OpenAIVision[OpenAI GPT-4o Vision]
    VisionStrategy -->|No| TesseractOCR[Tesseract OCR Fallback]
    
    OpenAIVision --> OpenAISuccess{Extraction<br/>Successful?}
    OpenAISuccess -->|Yes| ParseOpenAI[Parse OpenAI Response]
    OpenAISuccess -->|No| TesseractOCR
    
    TesseractOCR --> PreprocessImage[Preprocess Image<br/>Convert to RGB]
    PreprocessImage --> RunOCR[Run Tesseract OCR]
    RunOCR --> TesseractSuccess{OCR Text<br/>Available?}
    
    TesseractSuccess -->|Yes| ParseTesseract[Parse OCR Text]
    TesseractSuccess -->|No| ExtractionFailed[Extraction Failed]
    
    ParseOpenAI --> ExtractTitle[Extract Book Title]
    ParseTesseract --> ExtractTitle
    
    ExtractTitle --> ExtractISBN[Extract ISBN<br/>13-digit pattern]
    ExtractISBN --> CleanupTemp[Cleanup Temporary Files]
    
    CleanupTemp --> ValidationStep{Title and ISBN<br/>Valid?}
    ValidationStep -->|Yes| ReturnResults[Return Title and ISBN]
    ValidationStep -->|No| PartialResults[Return Partial Results]
    
    ReturnResults --> End([End: Success])
    PartialResults --> End
    ExtractionFailed --> ErrorEnd([End: Failed])
    SizeError --> ErrorEnd
    FormatError --> ErrorEnd
```

## 3. AI Enrichment Process

This activity diagram shows how the system enriches book records with AI-powered metadata.

```mermaid
flowchart TD
    Start([Start: Enrichment Request]) --> LoadRecords[Load All Book Records]
    LoadRecords --> FilterRecords[Filter Records Needing Enrichment]
    
    FilterRecords --> HasRecords{Records to<br/>Process?}
    HasRecords -->|No| NoWork[No Enrichment Needed]
    HasRecords -->|Yes| StartLoop[Begin Processing Loop]
    
    StartLoop --> NextRecord[Get Next Record]
    NextRecord --> CheckTitle{Title<br/>Available?}
    
    CheckTitle -->|No| SkipRecord[Skip Record]
    CheckTitle -->|Yes| PreparePrompt[Prepare AI Prompt]
    
    PreparePrompt --> CallOpenAI[Call OpenAI GPT-4o]
    CallOpenAI --> APISuccess{API Call<br/>Successful?}
    
    APISuccess -->|No| LogError[Log API Error]
    APISuccess -->|Yes| ParseResponse[Parse AI Response]
    
    ParseResponse --> ExtractURLs[Extract Amazon URLs]
    ExtractURLs --> ValidateURLs{URLs Valid<br/>Format?}
    
    ValidateURLs -->|Yes| UpdateRecord[Update Record with URLs]
    ValidateURLs -->|No| LogWarning[Log Invalid URLs]
    
    UpdateRecord --> CheckPrices{Purchase & Used<br/>Prices Available?}
    LogWarning --> CheckPrices
    LogError --> CheckPrices
    SkipRecord --> CheckPrices
    
    CheckPrices -->|Yes| CalculatePriceRatio[Calculate Price Ratio]
    CheckPrices -->|No| RecalculateDecision[Recalculate Decision]
    
    CalculatePriceRatio --> MapToVScore[Map Ratio to V Score<br/>0-5 scale]
    MapToVScore --> UpdateVScore[Update V Score]
    UpdateVScore --> RecalculateDecision
    
    RecalculateDecision --> CalculateUtilities[Calculate New Utilities]
    CalculateUtilities --> UpdateDecision[Update Decision]
    UpdateDecision --> MoreRecords{More Records<br/>to Process?}
    
    MoreRecords -->|Yes| NextRecord
    MoreRecords -->|No| SaveAll[Save All Updated Records]
    
    SaveAll --> GenerateReport[Generate Summary Report]
    GenerateReport --> End([End: Enrichment Complete])
    NoWork --> End
```

## 4. CLI Batch Processing Workflow

This activity diagram illustrates the command-line batch processing workflow.

```mermaid
flowchart TD
    Start([Start: CLI Command]) --> ParseArgs[Parse Command Arguments]
    ParseArgs --> ValidateArgs{Arguments<br/>Valid?}
    
    ValidateArgs -->|No| ShowHelp[Show Usage Help]
    ValidateArgs -->|Yes| CheckCommand{Which<br/>Command?}
    
    CheckCommand -->|scan| ScanCommand[Scan Command]
    CheckCommand -->|web| WebCommand[Web Command]
    CheckCommand -->|create-csv| CreateCommand[Create CSV Command]
    CheckCommand -->|info| InfoCommand[Info Command]
    
    %% Scan Command Flow
    ScanCommand --> CheckCSV{CSV File<br/>Exists?}
    CheckCSV -->|No| CreateNewCSV[Create New CSV]
    CheckCSV -->|Yes| LoadCSV[Load Existing CSV]
    
    CreateNewCSV --> InitializeTriage[Initialize BookTriage]
    LoadCSV --> InitializeTriage
    
    InitializeTriage --> GetRecords[Get All Records]
    GetRecords --> HasWork{Records Need<br/>Processing?}
    
    HasWork -->|No| NoProcessing[No Processing Needed]
    HasWork -->|Yes| StartEnrichment[Start Enrichment Process]
    
    StartEnrichment --> ProcessLoop[Process Each Record]
    ProcessLoop --> EnrichComplete[Enrichment Complete]
    EnrichComplete --> SaveResults[Save Updated Records]
    SaveResults --> ShowSummary[Show Processing Summary]
    
    %% Web Command Flow
    WebCommand --> InitializeWeb[Initialize Web App]
    InitializeWeb --> StartServer[Start Uvicorn Server]
    StartServer --> ServerRunning[Server Running]
    ServerRunning --> WaitForShutdown[Wait for Shutdown Signal]
    
    %% Create CSV Command Flow
    CreateCommand --> SampleData{Include Sample<br/>Data?}
    SampleData -->|Yes| CreateWithSamples[Create CSV with Samples]
    SampleData -->|No| CreateEmpty[Create Empty CSV]
    
    CreateWithSamples --> CSVCreated[CSV File Created]
    CreateEmpty --> CSVCreated
    
    %% Info Command Flow
    InfoCommand --> ReadCSV[Read CSV File]
    ReadCSV --> AnalyzeData[Analyze Data]
    AnalyzeData --> ShowStats[Show Statistics]
    
    %% Common Endpoints
    ShowHelp --> End([End: Help Shown])
    NoProcessing --> End
    ShowSummary --> End([End: Scan Complete])
    WaitForShutdown --> End([End: Server Stopped])
    CSVCreated --> End([End: CSV Created])
    ShowStats --> End([End: Info Displayed])
```

## 5. Web Interface Request Processing

This activity diagram shows how web requests are processed through the FastAPI application.

```mermaid
flowchart TD
    Start([Start: HTTP Request]) --> RouteRequest[Route Request to Endpoint]
    RouteRequest --> CheckAuth{Authentication<br/>Required?}
    
    CheckAuth -->|Yes| ValidateAuth[Validate HTTP Basic Auth]
    CheckAuth -->|No| CheckRate[Check Rate Limit]
    
    ValidateAuth --> AuthValid{Credentials<br/>Valid?}
    AuthValid -->|No| AuthError[Return 401 Unauthorized]
    AuthValid -->|Yes| CheckRate
    
    CheckRate --> RateOK{Within Rate<br/>Limits?}
    RateOK -->|No| RateError[Return 429 Rate Limited]
    RateOK -->|Yes| ProcessRequest{Request Type?}
    
    ProcessRequest -->|GET /| ServeHTML[Serve Main HTML Page]
    ProcessRequest -->|GET /books| GetBooks[Get Book List]
    ProcessRequest -->|POST /upload_photo| UploadPhoto[Upload Photo Endpoint]
    ProcessRequest -->|POST /add_manual_title| AddTitle[Add Manual Title]
    ProcessRequest -->|POST /scan| ScanBooks[Scan Books Endpoint]
    ProcessRequest -->|GET /health| HealthCheck[Health Check]
    
    %% Upload Photo Flow
    UploadPhoto --> ValidateFile[Validate Uploaded File]
    ValidateFile --> FileValid{File Valid?}
    FileValid -->|No| FileError[Return 400 Bad Request]
    FileValid -->|Yes| ProcessImage[Process Image with Vision]
    
    ProcessImage --> ImageSuccess{Image Processing<br/>Successful?}
    ImageSuccess -->|No| ProcessError[Return Processing Error]
    ImageSuccess -->|Yes| CreateBookRecord[Create New Book Record]
    
    CreateBookRecord --> SaveRecord[Save to CSV]
    SaveRecord --> ReturnSuccess[Return Success Response]
    
    %% Add Manual Title Flow
    AddTitle --> ValidateInput[Validate Title and ISBN]
    ValidateInput --> InputValid{Input Valid?}
    InputValid -->|No| InputError[Return 400 Bad Request]
    InputValid -->|Yes| CreateManualRecord[Create Book Record]
    
    CreateManualRecord --> EnrichRecord[Enrich with AI]
    EnrichRecord --> SaveManualRecord[Save to CSV]
    SaveManualRecord --> ReturnCreated[Return Created Response]
    
    %% Get Books Flow
    GetBooks --> LoadAllRecords[Load All Records from CSV]
    LoadAllRecords --> FormatResponse[Format JSON Response]
    FormatResponse --> ReturnBooks[Return Book List]
    
    %% Scan Books Flow (Admin)
    ScanBooks --> CheckAdminAuth[Check Admin Authorization]
    CheckAdminAuth --> AdminValid{Admin<br/>Authorized?}
    AdminValid -->|No| AdminError[Return 403 Forbidden]
    AdminValid -->|Yes| StartBatchScan[Start Batch Scan Process]
    
    StartBatchScan --> BatchComplete[Batch Processing Complete]
    BatchComplete --> ReturnScanResult[Return Scan Results]
    
    %% Health Check Flow
    HealthCheck --> CheckDependencies[Check System Dependencies]
    CheckDependencies --> SystemHealthy{System<br/>Healthy?}
    SystemHealthy -->|Yes| ReturnHealthy[Return 200 OK]
    SystemHealthy -->|No| ReturnUnhealthy[Return 503 Service Unavailable]
    
    %% Common Endpoints
    ServeHTML --> AddSecurityHeaders[Add Security Headers]
    ReturnSuccess --> AddSecurityHeaders
    ReturnCreated --> AddSecurityHeaders
    ReturnBooks --> AddSecurityHeaders
    ReturnScanResult --> AddSecurityHeaders
    ReturnHealthy --> AddSecurityHeaders
    ReturnUnhealthy --> AddSecurityHeaders
    
    AddSecurityHeaders --> End([End: Response Sent])
    
    %% Error Endpoints
    AuthError --> End
    RateError --> End
    FileError --> End
    ProcessError --> End
    InputError --> End
    AdminError --> End
```

## Key Process Characteristics

### 1. **Fault Tolerance**
- Multiple fallback strategies for image processing
- Graceful degradation when external services fail
- Comprehensive error handling and logging

### 2. **Security Integration**
- Authentication checks at request entry points
- Input validation for all user-provided data
- Rate limiting to prevent abuse

### 3. **Dual Processing Modes**
- Interactive web interface for single-book operations
- Batch CLI processing for bulk operations
- Shared core logic between interfaces

### 4. **AI-Enhanced Workflows**
- Primary AI processing with fallback mechanisms
- Enrichment processes that enhance but don't block core functionality
- Configurable AI service integration

### 5. **Data Consistency**
- Atomic operations for data updates
- CSV file integrity maintained throughout processes
- Validation at multiple process stages

### 6. **User Experience Focus**
- Clear feedback at each process step
- Progress indication for long-running operations
- Helpful error messages with recovery suggestions

These activity diagrams demonstrate the Book Triage system's robust, user-friendly workflows that balance automation with user control while maintaining data integrity and system reliability. 