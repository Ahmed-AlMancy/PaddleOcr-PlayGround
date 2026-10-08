import os
import json
import random

MERMAID_DIR = "docs/diagrams/mermaid"
EXCALIDRAW_DIR = "docs/diagrams/excalidraw"

os.makedirs(MERMAID_DIR, exist_ok=True)
os.makedirs(EXCALIDRAW_DIR, exist_ok=True)

# -------------------------------------------------------------------
# MERMAID DEFINITIONS FOR ALL 15 DIAGRAMS
# -------------------------------------------------------------------

mermaid_diagrams = {
    "01_system_overview": """%% Diagram 01: System Overview (High-Level End-to-End Flow)
%% Status: CURRENT
flowchart TD
    classDef actorStyle fill:#1e293b,color:#f8fafc,stroke:#3b82f6,stroke-width:2px;
    classDef engineStyle fill:#0f172a,color:#38bdf8,stroke:#0284c7,stroke-width:2px;
    classDef procStyle fill:#14532d,color:#86efac,stroke:#22c55e,stroke-width:2px;
    classDef aiStyle fill:#4c1d95,color:#c084fc,stroke:#a855f7,stroke-width:2px;
    classDef storeStyle fill:#854d0e,color:#fef08a,stroke:#eab308,stroke-width:2px;

    User[User / External System]:::actorStyle -->|Input Image .jpg/.png or JSON| Interface[Receipt Processing API / CLI run.py]:::engineStyle
    Interface -->|Raw Input File Path| Preproc[Image Preprocessing & Digit Normalization]:::procStyle
    Preproc -->|Cleaned Image / JSON| OCR[PaddleOCR Engine PP-OCRv5]:::engineStyle
    OCR -->|Raw Text Boxes & Coordinates| Spatial[Spatial Layout & Reading Order Parser]:::procStyle
    Spatial -->|Deterministic Structured Receipt| ConfEval[OCR Confidence & Layout Quality Evaluator]:::procStyle
    ConfEval -->|Valid Spatial Layout| SemanticLLM[Local LLM Semantic Correction qwen2.5:3b]:::aiStyle
    SemanticLLM -->|Enriched JSON Dict| Validation[Domain Receipt Validator & Category Guard]:::procStyle
    Validation -->|Final Validated Receipt| Output[Structured Receipt JSON Output Artifact]:::storeStyle
    Output -->|Expense Reports / API Response| ExternalConsumer[Database / Expense Report Applications]:::storeStyle
""",

    "02_detailed_processing_pipeline": """%% Diagram 02: Detailed Processing Pipeline Technical Data Flow
%% Status: CURRENT
flowchart TD
    subgraph Step1["Step 1: Input & OCR Extraction"]
        Image[Receipt Image File / JSON] -->|Input Path| OCR_Engine[PaddleOcrEngine PP-OCRv5]
        OCR_Engine -->|Extract| Raw_Detections[Raw OCR Detections: text, confidence, bounding_box]
    end

    subgraph Step2["Step 2: Coordinate Normalization & Preprocessing"]
        Raw_Detections -->|prepare_ocr_elements| Preproc[ReceiptPreprocessor]
        Preproc -->|Eastern Arabic Translation ٠-٩ -> 0-9| Digits[Normalized Ascii Digits]
        Preproc -->|Centroid Calculation| Centroid[center_x, center_y]
        Preproc -->|Top-to-Bottom Sort| OcrElements[List of OcrElement Objects]
    end

    subgraph Step3["Step 3: Deterministic Spatial Layout Parsing"]
        OcrElements --> SpatialParser[SpatialLayoutParser.parse]
        SpatialParser --> Header[Detect Table Header Row Y]
        SpatialParser --> Merchant[Extract Merchant Name above Table]
        SpatialParser --> Meta[Extract Receipt No, Date, Time, Currency, Payment Method]
        SpatialParser --> Totals[Extract Subtotal, Discount, Service Charge, Tax, Total]
        SpatialParser --> LinePairing[RTL Leftmost vs LTR Rightmost Price-to-Item Pairing]
        LinePairing --> InitialReceipt[StructuredReceipt Domain Entity]
    end

    subgraph Step4["Step 4: Semantic LLM Correction & Validation"]
        InitialReceipt --> LLMClient[OllamaLlmClient qwen2.5:3b]
        LLMClient -->|Local Subprocess Call| LLM_Response[Raw LLM JSON Dict]
        LLM_Response --> Validator[ReceiptValidator]
        Validator -->|Category Mapping & Spatial Fallback Protection| ValidatedReceipt[Validated StructuredReceipt Entity]
        ValidatedReceipt -->|to_dict| FinalJSON[receipt_output.json File]
    end
""",

    "03_ocr_and_layout": """%% Diagram 03: OCR & Spatial Layout Understanding
%% Status: CURRENT
flowchart TD
    subgraph InputStage["1. Raw OCR Detection"]
        Img[Receipt Image] --> PaddleOCR[PaddleOCR Engine PP-OCRv5]
        PaddleOCR --> Detections["OCR Detections list:<br/>- text: str<br/>- confidence: float<br/>- box: [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]"]
    end

    subgraph LayoutStage["2. Spatial Grid Transformation"]
        Detections --> CentroidMath["Centroid Calculation:<br/>center_x = mean(points_x)<br/>center_y = mean(points_y)"]
        CentroidMath --> RowClustering["Row Clustering:<br/>y_bucket = center_y // 15"]
        RowClustering --> ColumnClustering["Column Clustering & Alignment:<br/>Sort items by center_x"]
        ColumnClustering --> ReadingOrder["Reading Order Sort:<br/>sort(key = lambda x: (x.center_y, x.center_x))"]
        ReadingOrder --> ReceiptLayout["ReceiptLayout Grid (OcrElements)"]
    end

    subgraph ExampleGrid["3. Spatial Alignment Representation"]
        ReceiptLayout --> IllustrativeExample["Illustrative RTL Arabic Layout Grid:<br/>----------------------------------------<br/>ITEM (Far Right)          PRICE (Far Left)<br/>مياه معدنية                    2.00<br/>شطيرة                          5.00<br/>موز                            88.00<br/>----------------------------------------"]
    end
""",

    "04_receipt_parsing": """%% Diagram 04: Receipt Parsing & Financial Field Association
%% Status: CURRENT
flowchart TD
    Layout[ReceiptLayout Grid OcrElements] --> HeaderDet[1. Table Header Detection detect_table_header_y]
    HeaderDet --> MerchantDet[2. Merchant Extraction extract_merchant_name]
    MerchantDet --> ItemPairing[3. Item & Price Spatial Line Pairing]
    
    ItemPairing --> FinancialFields["4. Financial Breakdown Extraction (Nullable Schema)"]
    
    subgraph FinancialBreakdown["Financial Breakdown Schema"]
        FinancialFields --> Subtotal["subtotal: Optional[float] (NULL if missing)"]
        FinancialFields --> Discount["discount: Optional[float] (NULL if missing)"]
        FinancialFields --> Service["service_charge: Optional[float] (NULL if missing)"]
        FinancialFields --> Tax["tax: Optional[float] (NULL if missing)"]
        FinancialFields --> Total["total: Optional[float] (NULL if missing)"]
        FinancialFields --> Currency["currency: Optional[str] (e.g. SAR, EGP, USD)"]
    end

    FinancialBreakdown --> PaymentDet["5. Payment Info Extraction (Cash / Card)"]
    PaymentDet --> DomainModel[StructuredReceipt Domain Entity]
""",

    "05_llm_and_vision_fallback": """%% Diagram 05: LLM & Vision Fallback Architecture
%% Status: CURRENT (Text LLM) vs PLANNED (Vision LLM Fallback)
flowchart TD
    classDef current fill:#14532d,color:#86efac,stroke:#22c55e,stroke-width:2px;
    classDef planned fill:#451a03,color:#fdba74,stroke:#f97316,stroke-width:2px,stroke-dasharray: 5 5;

    OCR[PaddleOCR & Spatial Layout Engine]:::current --> Parse[Parsed Spatial Receipt]:::current
    Parse --> Evaluator[Confidence & Quality Evaluator]:::current

    Evaluator -->|High Confidence / Good Layout| GoodPath{Is Confidence High?}:::current
    
    subgraph NormalPath["Normal Execution Path [CURRENT]"]
        GoodPath -->|YES| TextLLM[Ollama Local Text LLM qwen2.5:3b]:::current
        TextLLM --> TextValid[ReceiptValidator Category & Typo Normalization]:::current
        TextValid --> SuccessOutput[Final Validated Structured Receipt]:::current
    end

    subgraph FallbackPath["Vision AI Fallback Path [PLANNED / FUTURE]"]
        GoodPath -.->|NO: Low Confidence / Bad Pairing / Image Distortion| VisionTrigger[Vision Fallback Trigger]:::planned
        VisionTrigger -.-> Reasons["Fallback Reasons:<br/>- Low OCR Confidence (< 0.6)<br/>- Unpaired Orphan Numbers > 3<br/>- Missing Subtotal/Total Math Match<br/>- Severely Distorted / Rotated Image"]:::planned
        Reasons -.-> VisionLLM[Vision LLM Engine e.g. Qwen2-VL / PaddleOCR-VL]:::planned
        VisionLLM -.-> VisionValid[ReceiptValidator Schema Enforcement]:::planned
        VisionValid -.-> SuccessOutput:::current
    end
""",

    "06_domain_model": """%% Diagram 06: Domain Model Entity Relationships & Field Schemas
%% Status: CURRENT
classDiagram
    class BoundingBox {
        +List~List~float~~ points
        +float center_x
        +float center_y
    }

    class OcrElement {
        +str text
        +float confidence
        +List~List~float~~ box
        +float center_x
        +float center_y
        +bool is_number
        +bool contains_arabic
    }

    class ReceiptItem {
        +str original_ocr
        +str name
        +Optional~float~ price
        +str category
        +float correction_confidence
        +to_dict() Dict
    }

    class StructuredReceipt {
        +Optional~str~ merchant
        +Optional~str~ receipt_number
        +Optional~str~ date
        +Optional~str~ time
        +Optional~str~ currency
        +Optional~str~ payment_method
        +List~ReceiptItem~ items
        +Optional~float~ subtotal
        +Optional~float~ discount
        +Optional~float~ service_charge
        +Optional~float~ tax
        +Optional~float~ total
        +to_dict() Dict
    }

    class CategoryValidator {
        +List~str~ ALLOWED_CATEGORIES
        +validate_category(raw_category) str
    }

    class ReceiptPreprocessor {
        +normalize_digits(text) str
        +clean_price_str(text) str
        +parse_number_value(text) Optional~float~
        +strip_quantity_prefix(text) str
        +prepare_ocr_elements(raw_items) List~OcrElement~
    }

    class ReceiptValidator {
        +validate_receipt_dict(raw_dict, original_receipt) StructuredReceipt
        +validate_item_dict(raw_item, fallback_ocr, fallback_price) ReceiptItem
    }

    StructuredReceipt "1" *-- "*" ReceiptItem : contains
    ReceiptPreprocessor ..> OcrElement : generates
    ReceiptValidator ..> StructuredReceipt : validates
    CategoryValidator ..> ReceiptItem : categorizes
""",

    "07_validation_and_error_handling": """%% Diagram 07: Validation & Error Handling Architecture
%% Status: CURRENT
flowchart TD
    classDef pass fill:#14532d,color:#86efac,stroke:#22c55e;
    classDef fail fill:#7f1d1d,color:#fca5a5,stroke:#ef4444;
    classDef recover fill:#1e293b,color:#f8fafc,stroke:#3b82f6;

    Start[Input Receipt Process Call] --> CheckFile{Does File Exist?}
    CheckFile -->|No| ErrFileNotFound[Raise FileNotFoundError - STOP]:::fail
    CheckFile -->|Yes| OCRRun[Execute OCR Engine]

    OCRRun --> CheckOCRText{Any OCR Text Detected?}
    CheckOCRText -->|No| ReturnEmpty[Return Empty StructuredReceipt JSON - SAFE FALLBACK]:::recover
    CheckOCRText -->|Yes| ParseSpatial[Run Spatial Layout Parser]

    ParseSpatial --> CheckLLM{Is LLM Enabled & Running?}
    CheckLLM -->|No / CLI Flag --no-llm| SkipLLM[Use Spatial Parsed Receipt directly]:::pass
    CheckLLM -->|Yes| CallLLM[Execute Ollama Subprocess]

    CallLLM --> CheckLLMExec{LLM Subprocess Success?}
    CheckLLMExec -->|Subprocess Timeout / Error| LLMFailFallback[Fallback to Spatial Parsed Receipt without LLM]:::recover
    CheckLLMExec -->|Returns Output| ParseJSON{Valid JSON Response?}

    ParseJSON -->|Malformed JSON / Syntax Error| JSONFailFallback[Restore Spatial Parsed Receipt & Original OCR Prices]:::recover
    ParseJSON -->|Valid JSON| ValidateSchema[ReceiptValidator]

    ValidateSchema --> CheckCategory{Is Category Allowed?}
    CheckCategory -->|Invalid Category| CategoryFallback[Set category = 'Other']:::recover
    CheckCategory -->|Valid Category| RetainCategory[Retain Category]:::pass

    ValidateSchema --> CheckDroppedItems{Did LLM Drop Line Items/Prices?}
    CheckDroppedItems -->|Yes| RestoreSpatialData[Merge Spatial Original OCR & Price back into Item]:::recover
    CheckDroppedItems -->|No| FinalResult[Return Validated Receipt JSON]:::pass

    SkipLLM --> FinalResult
    ReturnEmpty --> FinalResult
    LLMFailFallback --> FinalResult
    JSONFailFallback --> FinalResult
""",

    "08_project_architecture": """%% Diagram 08: Project Package Architecture & Dependency Directions
%% Status: CURRENT
flowchart TD
    subgraph Presentation["Presentation Layer (Outer)"]
        CLI[receipt_processor.presentation.cli]
        API[receipt_processor.presentation.api]
        RunScript[run.py]
    end

    subgraph UseCases["Use Cases / Application Layer"]
        ProcessUC[receipt_processor.use_cases.process_receipt.ProcessReceiptUseCase]
        SpatialParser[receipt_processor.use_cases.spatial_parser.SpatialLayoutParser]
    end

    subgraph Contracts["Contracts Layer (Abstractions / Interfaces)"]
        IOCREngine[receipt_processor.contracts.ocr_engine.IOCREngine]
        ILLMClient[receipt_processor.contracts.llm_client.ILLMClient]
    end

    subgraph Domain["Domain Layer (Core Business Rules - Zero External Dependencies)"]
        Models[receipt_processor.domain.models]
        Preprocessor[receipt_processor.domain.preprocessor]
        Validator[receipt_processor.domain.validator]
        CategoryRules[receipt_processor.domain.category_rules]
        LayoutCalc[receipt_processor.domain.layout_calculator]
    end

    subgraph Infrastructure["Infrastructure Layer (External Tool Implementations)"]
        PaddleEngine[receipt_processor.infrastructure.paddle_ocr_engine.PaddleOcrEngine]
        JsonLoader[receipt_processor.infrastructure.json_ocr_loader.JsonOcrLoader]
        OllamaClient[receipt_processor.infrastructure.ollama_llm_client.OllamaLlmClient]
    end

    RunScript --> API
    CLI --> API
    API --> ProcessUC
    ProcessUC --> SpatialParser
    ProcessUC --> IOCREngine
    ProcessUC --> ILLMClient
    ProcessUC --> Domain

    SpatialParser --> Domain
    PaddleEngine -. Implements .-> IOCREngine
    JsonLoader -. Implements .-> IOCREngine
    OllamaClient -. Implements .-> ILLMClient

    Infrastructure --> Domain
""",

    "09_end_to_end_sequence": """%% Diagram 09: End-to-End Processing Sequence Diagram
%% Status: CURRENT
sequenceDiagram
    autonumber
    actor User
    participant CLI as presentation/cli.py
    participant API as presentation/api.py
    participant UC as ProcessReceiptUseCase
    participant OCR as PaddleOcrEngine
    participant PP as ReceiptPreprocessor
    participant SP as SpatialLayoutParser
    participant LLM as OllamaLlmClient
    participant VAL as ReceiptValidator

    User->>CLI: Run python run.py receipt.jpg
    CLI->>API: process_receipt(input_path="receipt.jpg", use_llm=True)
    API->>UC: ProcessReceiptUseCase.execute(input_path="receipt.jpg")
    
    rect rgb(30, 41, 59)
        Note over UC,OCR: 1. OCR Extraction Phase
        UC->>OCR: extract_text("receipt.jpg", lang="ar")
        OCR-->>UC: raw_ocr_items [{text, confidence, box}]
    end

    rect rgb(15, 23, 42)
        Note over UC,PP: 2. Preprocessing & Normalization Phase
        UC->>PP: prepare_ocr_elements(raw_ocr_items)
        PP->>PP: Normalize digits (٠-٩ -> 0-9) & compute centroids
        PP-->>UC: sorted List[OcrElement]
    end

    rect rgb(20, 83, 45)
        Note over UC,SP: 3. Spatial Layout Parsing Phase
        UC->>SP: parse(prepared_ocr)
        SP->>SP: Detect table headers, merchant, date/time, totals
        SP->>SP: Match items & prices (RTL vs LTR spatial pairing)
        SP-->>UC: parsed_receipt (StructuredReceipt Domain Entity)
    end

    rect rgb(76, 29, 149)
        Note over UC,VAL: 4. LLM Enrichment & Validation Phase
        UC->>LLM: process_semantic_receipt(parsed_receipt)
        LLM->>LLM: Execute local ollama subprocess qwen2.5:3b
        LLM-->>UC: raw_llm_json_dict
        UC->>VAL: validate_receipt_dict(raw_llm_json_dict, original_receipt=parsed_receipt)
        VAL-->>UC: final_receipt (StructuredReceipt Domain Entity)
    end

    UC-->>API: final_dict
    API-->>CLI: final_dict
    CLI-->>User: Print JSON Output & Save to receipt_output.json
""",

    "10_data_lifecycle": """%% Diagram 10: Data Lifecycle & Transformation Pipeline
%% Status: CURRENT
flowchart TD
    Stage1["1. Receipt Image File (.jpg / .png)<br/>Raw RGB Image Pixels"] --> Stage2["2. Raw OCR Detections List<br/>Dict: {text: str, confidence: float, box: [[x,y],...]}"]
    Stage2 --> Stage3["3. Normalized OcrElements List<br/>OcrElement: {text, confidence, center_x, center_y, is_number, contains_arabic}"]
    Stage3 --> Stage4["4. Initial Parsed Receipt Entity<br/>StructuredReceipt: {merchant, date, items: [ReceiptItem], subtotal, tax, total}"]
    Stage4 --> Stage5["5. Prompt JSON String<br/>Structured Prompt with ALLOWED_CATEGORIES passed to Ollama"]
    Stage5 --> Stage6["6. Raw LLM Response Dict<br/>Dict: {merchant, items: [{name, price, category}], total}"]
    Stage6 --> Stage7["7. Validated Domain Entity<br/>StructuredReceipt: Corrected categories, restored original prices, validated schema"]
    Stage7 --> Stage8["8. Output JSON Artifact<br/>receipt_output.json formatted JSON file"]
""",

    "11_benchmark_architecture": """%% Diagram 11: Benchmark Runner Architecture & Model Comparison
%% Status: CURRENT
flowchart TD
    Dataset[Receipt Test Dataset receipt.jpg, receipt10.jpg, receipt11.jpg...] --> BenchRunner[Benchmark Runner tests/benchmark_ocr.py]

    subgraph ProductionPipeline["Production Engine: PP-OCRv5 + Spatial Parser"]
        BenchRunner --> Engine1[PaddleOcrEngine PP-OCRv5]
        Engine1 --> Spatial1[SpatialLayoutParser + Ollama]
        Spatial1 --> Results1["Metrics:<br/>- Processing Time (sec)<br/>- RAM Usage (MB)<br/>- OCR Boxes Count<br/>- Items Count & Merchant"]
    end

    subgraph ExperimentalEngine["Experimental Engine: PP-StructureV3"]
        BenchRunner --> Engine2[PP-StructureV3 Layout Pipeline]
        Engine2 --> Results2["CPU pir::ArrayAttribute Bug Exception Logged:<br/>ConvertPirAttribute2RuntimeAttribute error"]
    end

    Results1 --> OutputArtifacts[Benchmark Artifacts]
    Results2 --> OutputArtifacts

    subgraph Artifacts["Generated Reports"]
        OutputArtifacts --> ReportJSON[benchmark_report.json]
        OutputArtifacts --> ResultJSON[ocr_result.json]
        OutputArtifacts --> MarkdownReport[ocr_benchmark_report.md]
    end
""",

    "12_test_architecture": """%% Diagram 12: Automated Test Architecture & Pytest Suite
%% Status: CURRENT
flowchart TD
    PytestRunner[Pytest Test Runner python -m pytest] --> TestSuite[tests/test_pipeline.py]

    subgraph Helpers["Test Data Generators"]
        TestSuite --> SyntheticGen[create_synthetic_ocr_data helper]
        SyntheticGen --> SyntheticOCR[Synthetic OcrElement Box Stream]
    end

    subgraph TestCases["Test Suites (11 Passing Tests)"]
        TestSuite --> CatTests["1. Category Validation Tests:<br/>- Exact categories<br/>- Case insensitivity<br/>- Invalid fallbacks"]
        TestSuite --> PreprocTests["2. Preprocessing & Digit Tests:<br/>- Eastern Arabic digits ٠-٩<br/>- Price cleaning & trailing artifact 17.0C<br/>- Weight prefix stripping"]
        TestSuite --> SpatialTests["3. Spatial Matching Tests:<br/>- Synthetic horizontal alignment<br/>- Arabic RTL leftmost price selection<br/>- Discount & Service charge parsing"]
        TestSuite --> PipelineTests["4. Full Integration Tests:<br/>- Offline receipt execution<br/>- Null financial field retention"]
    end

    TestCases --> Assertions["Assertions & Validation:<br/>100% Passing Status (11/11 Passed)"]
""",

    "13_configuration_and_dependencies": """%% Diagram 13: Configuration Management & System Dependencies
%% Status: CURRENT
flowchart TD
    subgraph SystemConfig["System Configuration (receipt_processor/config.py)"]
        ConfigDefaults["Defaults:<br/>- DEFAULT_OLLAMA_MODEL = 'qwen2.5:3b'<br/>- Default Output = 'receipt_output.json'<br/>- Default OCR Lang = 'ar'<br/>- LLM Timeout = 60s"]
    end

    subgraph EnvVars["Environment Flags"]
        EnvFlags["Environment Variables:<br/>- FLAGS_enable_pir_api = 0<br/>- FLAGS_use_mkldnn = 0<br/>- PADDLE_SERVO_MODE"]
    end

    subgraph RuntimeDeps["Python Package Dependencies (.venv)"]
        Deps["Core Packages:<br/>- Python 3.12<br/>- paddlepaddle (v3.3.1 CPU)<br/>- paddleocr (v3.7.0 / PP-OCRv5)<br/>- pytest (v9.1.1)<br/>- dataclasses & typing"]
    end

    subgraph ExternalBinaries["External Executables"]
        Binaries["Local Binaries:<br/>- Ollama CLI (ollama.exe)<br/>- Local LLM Weights (qwen2.5:3b)"]
    end

    ConfigDefaults --> PipelineExecution[ProcessReceiptUseCase execution]
    EnvFlags --> PipelineExecution
    RuntimeDeps --> PipelineExecution
    ExternalBinaries --> PipelineExecution
""",

    "14_deployment_runtime": """%% Diagram 14: Deployment Runtime & Hardware Process Topology
%% Status: CURRENT
flowchart TD
    subgraph HostOS["Windows Workstation Host OS"]
        
        subgraph PythonEnv["Python Virtual Environment (.venv)"]
            MainProc["Main Python Process: python run.py<br/>(ProcessReceiptUseCase Orchestrator)"]
            
            subgraph PaddleRuntime["In-Process Paddle C++ Predictor"]
                PP_Engine["PP-OCRv5 Detection & Recognition Models<br/>(CPU Static Graph Inference via oneDNN)"]
            end
        end

        subgraph LocalSubprocess["External Local Process"]
            OllamaProc["Ollama Process: ollama.exe<br/>(qwen2.5:3b LLM Local Inference)"]
        end

        subgraph Hardware["Hardware Resources"]
            CPU["Intel / AMD CPU (Active Processing)"]
            RAM["System RAM (PaddleOCR & LLM Memory)"]
            GPU["NVIDIA GeForce GTX 1660 Ti 6GB VRAM<br/>(Available for GPU Paddle / CUDA builds)"]
        end
    end

    MainProc --> PP_Engine
    MainProc -->|Subprocess CLI Pipe| OllamaProc
    PP_Engine --> CPU
    OllamaProc --> RAM
""",

    "15_future_vision_pipeline": """%% Diagram 15: Planned Future Architecture Roadmap
%% Status: PLANNED / FUTURE
flowchart TD
    classDef current fill:#14532d,color:#86efac,stroke:#22c55e,stroke-width:2px;
    classDef future fill:#451a03,color:#fdba74,stroke:#f97316,stroke-width:2px,stroke-dasharray: 5 5;

    subgraph CurrentSystem["Current Operational System"]
        CLI[CLI & Local Python Script]:::current --> LocalEngine[PP-OCRv5 + SpatialParser + Ollama]:::current
        LocalEngine --> OutputJSON[Local JSON Files]:::current
    end

    subgraph FutureRoadmap["Planned Future Enhancements [FUTURE]"]
        WebAPI[FastAPI REST Web Service Endpoint]:::future --> TaskQueue[Async Worker Queue / Celery]:::future
        TaskQueue --> VisionFallback[Vision LLM Multimodal Pipeline Qwen2-VL]:::future
        TaskQueue --> GPUInference[PP-StructureV3 GPU / PIR Native Execution]:::future
        VisionFallback --> DBStore[SQLite / PostgreSQL Expense DB Storage]:::future
        GPUInference --> DBStore
        DBStore --> AnalyticsDashboard[Expense Analytics & Web UI Dashboard]:::future
    end

    CurrentSystem -. Refactor into .-> FutureRoadmap
"""
}

# -------------------------------------------------------------------
# EXCALIDRAW JSON GENERATOR FUNCTION
# -------------------------------------------------------------------

def generate_excalidraw_json(title: str, mmd_text: str) -> str:
    """Generates valid, schema-compliant Excalidraw JSON representing the diagram visually."""
    elements = []
    element_id_counter = 1

    # Extract nodes/lines from mermaid text to create visual boxes and text labels
    lines = [l.strip() for l in mmd_text.splitlines() if l.strip() and not l.strip().startswith("%%") and not l.strip().startswith("subgraph") and not l.strip().startswith("end") and not l.strip().startswith("classDef")]

    # Layout grid parameters
    start_x = 100
    start_y = 100
    box_width = 320
    box_height = 70
    y_gap = 110

    current_y = start_y

    # Add Diagram Title Note at top
    title_rect_id = f"rect_{element_id_counter}"
    title_text_id = f"text_{element_id_counter}"
    element_id_counter += 1

    elements.append({
        "id": title_rect_id,
        "type": "rectangle",
        "x": start_x,
        "y": current_y,
        "width": 640,
        "height": 50,
        "angle": 0,
        "strokeColor": "#1e293b",
        "backgroundColor": "#3b82f6",
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "index": f"a{element_id_counter}",
        "roundness": {"type": 3},
        "seed": random.randint(10000, 99999),
        "version": 1,
        "versionNonce": 1,
        "isDeleted": False,
        "boundElements": None,
        "updated": 1700000000000,
        "link": None,
        "locked": False
    })

    elements.append({
        "id": title_text_id,
        "type": "text",
        "x": start_x + 20,
        "y": current_y + 15,
        "width": 600,
        "height": 20,
        "angle": 0,
        "strokeColor": "#ffffff",
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "index": f"b{element_id_counter}",
        "roundness": None,
        "seed": random.randint(10000, 99999),
        "version": 1,
        "versionNonce": 1,
        "isDeleted": False,
        "boundElements": None,
        "updated": 1700000000000,
        "link": None,
        "locked": False,
        "text": f"Architecture Diagram: {title.replace('_', ' ').title()}",
        "fontSize": 18,
        "fontFamily": 1,
        "textAlign": "left",
        "verticalAlign": "middle",
        "containerId": None,
        "originalText": f"Architecture Diagram: {title.replace('_', ' ').title()}",
        "lineHeight": 1.2,
        "baseline": 15
    })

    current_y += 80

    # Create visual component nodes
    node_lines = [l for l in lines if "[" in l or "-->" in l or "class" in l][:8]
    if not node_lines:
        node_lines = [f"Component {i+1}" for i in range(5)]

    prev_rect_id = None
    prev_y = None

    for idx, raw_line in enumerate(node_lines):
        clean_name = raw_line.replace("[", " ").replace("]", " ").replace("-->", " -> ").replace(":::", " ").strip()
        if len(clean_name) > 60:
            clean_name = clean_name[:57] + "..."

        rect_id = f"rect_node_{idx}"
        text_id = f"text_node_{idx}"

        elements.append({
            "id": rect_id,
            "type": "rectangle",
            "x": start_x + (150 if idx % 2 == 1 else 0),
            "y": current_y,
            "width": box_width,
            "height": box_height,
            "angle": 0,
            "strokeColor": "#0f172a",
            "backgroundColor": "#f1f5f9" if idx % 2 == 0 else "#e2e8f0",
            "fillStyle": "solid",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "index": f"c{idx}",
            "roundness": {"type": 3},
            "seed": random.randint(10000, 99999),
            "version": 1,
            "versionNonce": 1,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1700000000000,
            "link": None,
            "locked": False
        })

        elements.append({
            "id": text_id,
            "type": "text",
            "x": start_x + (150 if idx % 2 == 1 else 0) + 15,
            "y": current_y + 20,
            "width": box_width - 30,
            "height": 30,
            "angle": 0,
            "strokeColor": "#0f172a",
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "index": f"d{idx}",
            "roundness": None,
            "seed": random.randint(10000, 99999),
            "version": 1,
            "versionNonce": 1,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1700000000000,
            "link": None,
            "locked": False,
            "text": clean_name[:40],
            "fontSize": 14,
            "fontFamily": 1,
            "textAlign": "center",
            "verticalAlign": "middle",
            "containerId": None,
            "originalText": clean_name[:40],
            "lineHeight": 1.2,
            "baseline": 12
        })

        # Add connector arrow between sequential components
        if prev_y is not None:
            arrow_id = f"arrow_{idx}"
            elements.append({
                "id": arrow_id,
                "type": "arrow",
                "x": start_x + 160,
                "y": prev_y + box_height,
                "width": 0,
                "height": y_gap - box_height,
                "angle": 0,
                "strokeColor": "#3b82f6",
                "backgroundColor": "transparent",
                "fillStyle": "solid",
                "strokeWidth": 2,
                "strokeStyle": "solid",
                "roughness": 1,
                "opacity": 100,
                "groupIds": [],
                "frameId": None,
                "index": f"e{idx}",
                "roundness": {"type": 2},
                "seed": random.randint(10000, 99999),
                "version": 1,
                "versionNonce": 1,
                "isDeleted": False,
                "boundElements": None,
                "updated": 1700000000000,
                "link": None,
                "locked": False,
                "points": [[0, 0], [0, y_gap - box_height]],
                "lastCommittedPoint": None,
                "startBinding": None,
                "endBinding": None,
                "startArrowhead": None,
                "endArrowhead": "arrow"
            })

        prev_y = current_y
        current_y += y_gap

    excalidraw_data = {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {
            "gridSize": 20,
            "viewBackgroundColor": "#ffffff"
        },
        "files": {}
    }

    return json.dumps(excalidraw_data, indent=2)

# Write all 15 Mermaid & Excalidraw files
for name, mmd_content in mermaid_diagrams.items():
    # 1. Write Mermaid file
    mmd_path = os.path.join(MERMAID_DIR, f"{name}.mmd")
    with open(mmd_path, "w", encoding="utf-8") as f:
        f.write(mmd_content.strip() + "\n")

    # 2. Write Excalidraw JSON file
    excal_path = os.path.join(EXCALIDRAW_DIR, f"{name}.excalidraw")
    excal_content = generate_excalidraw_json(name, mmd_content)
    with open(excal_path, "w", encoding="utf-8") as f:
        f.write(excal_content + "\n")

print("Generated 15 Mermaid files and 15 Excalidraw JSON files successfully.")
