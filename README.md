# Bilingual (Arabic/English) Receipt Expense Engine

An enterprise-grade, bilingually capable (Arabic & English) receipt processing and expense extraction pipeline built strictly following **Clean Architecture** and **SOLID Principles**.

---

## 📁 Repository Directory Structure

```text
receipt-test/
├── data/                       # Sample data & execution output artifacts
│   ├── images/                 # Receipt sample images (.jpg, .png)
│   └── outputs/                # Structured output JSONs & benchmark reports
├── docs/                       # Architecture diagrams & technical docs
│   ├── ARCHITECTURE.md         # High-level architecture overview
│   ├── DOCUMENTATION.md        # File-by-file technical reference
│   ├── diagrams/
│   │   ├── README.md           # Diagram index matrix & status guide
│   │   ├── excalidraw/         # 15 native Excalidraw (.excalidraw) JSON files
│   │   └── mermaid/            # 15 standalone Mermaid (.mmd) diagram files
│   └── legacy/                 # Legacy diagram files
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

## 🚀 Quick Start

### 1. Run Pipeline on Sample Image
```bash
python run.py data/images/receipt_07.jpg -o data/outputs/receipt_07_output.json
```

### 2. Run Automated Pytest Suite
```bash
python -m pytest
```

### 3. Run Performance Benchmark
```bash
python tests/benchmark_ocr.py
```

---

## 📖 Architecture & Diagrams

- **High-Level Overview:** See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- **Technical Reference:** See [`docs/DOCUMENTATION.md`](docs/DOCUMENTATION.md)
- **Visual Architecture Diagrams (15 Diagrams):** See [`docs/diagrams/README.md`](docs/diagrams/README.md)
