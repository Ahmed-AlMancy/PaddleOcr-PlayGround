# Bilingual (Arabic/English) Receipt Expense Engine

An enterprise-grade, bilingually capable (Arabic & English) receipt processing and expense extraction pipeline built strictly following **Clean Architecture** and **SOLID Principles**.

---

## 📁 Repository Directory Structure

```text
receipt-test/
├── data/                       # Sample data & execution output artifacts
│   ├── images/                 # Receipt sample images (.jpg, .png)
│   └── outputs/                # Structured output JSONs & benchmark reports
├── docs/                       # System architecture diagrams
│   └── diagrams/
│       ├── README.md           # Diagram index matrix & status guide
│       ├── excalidraw/         # 4 native Excalidraw (.excalidraw) JSON files
│       └── mermaid/            # 4 standalone Mermaid (.mmd) diagram files
├── receipt_processor/          # Core Clean Architecture Python package
│   ├── contracts/              # Inversion of Control interfaces (IOCREngine, ILLMClient)
│   ├── domain/                 # Domain entities, models, preprocessors & validators
│   ├── infrastructure/         # External integrations (PaddleOCR, Ollama LLM, JSON loader)
│   ├── presentation/           # CLI & API presentation layers
│   └── use_cases/              # Application orchestrator & Spatial Layout Engine
├── scripts/                    # Maintenance & generator scripts
│   └── generate_all_diagrams.py
├── tests/                      # Pytest automated test suite & benchmark runner
│   ├── test_pipeline.py        # 11 automated unit & integration tests
│   └── benchmark_ocr.py        # Pipeline benchmark performance harness
├── .gitignore
├── README.md                   # Main project repository guide
└── run.py                      # Top-level executable runner script
```

---

## 📖 System Architecture Diagrams

The project architecture is documented across 4 visual diagrams in both Mermaid (`.mmd`) and Excalidraw (`.excalidraw`) formats:

1. **`01_system_overview`**: High-level conceptual end-to-end processing pipeline.
2. **`02_detailed_processing_pipeline`**: Complete technical data flow between stages.
3. **`03_ocr_and_layout`**: Centroid normalization, row/column clustering & reading order.
4. **`04_receipt_parsing`**: Nullable financial breakdown & spatial line item matching.

See [`docs/diagrams/README.md`](docs/diagrams/README.md) for full diagram links and rendering instructions.
