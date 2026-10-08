# Receipt Processing Pipeline System Architecture Diagrams

This directory contains the comprehensive system architecture documentation for the **Bilingual (Arabic/English) Receipt Expense Processing Pipeline**.

Each diagram is provided in two formats:
1. **Mermaid (`.mmd`)**: Text-based diagram definition for rendering in GitHub Markdown, VS Code, or Mermaid Live Editor.
2. **Excalidraw (`.excalidraw`)**: Native, schema-compliant JSON file that can be opened directly in [Excalidraw](https://excalidraw.com).

---

## 1. Diagram Index & Status Matrix

| # | Diagram Name | Purpose | Status | Mermaid Path | Excalidraw Path |
|---|---|---|---|---|---|
| **01** | **System Overview** | High-level conceptual end-to-end processing pipeline | **CURRENT** | [`mermaid/01_system_overview.mmd`](mermaid/01_system_overview.mmd) | [`excalidraw/01_system_overview.excalidraw`](excalidraw/01_system_overview.excalidraw) |
| **02** | **Detailed Processing Pipeline** | Complete technical data flow between stages | **CURRENT** | [`mermaid/02_detailed_processing_pipeline.mmd`](mermaid/02_detailed_processing_pipeline.mmd) | [`excalidraw/02_detailed_processing_pipeline.excalidraw`](excalidraw/02_detailed_processing_pipeline.excalidraw) |
| **03** | **OCR & Layout Understanding** | Centroid normalization, row/column clustering & reading order | **CURRENT** | [`mermaid/03_ocr_and_layout.mmd`](mermaid/03_ocr_and_layout.mmd) | [`excalidraw/03_ocr_and_layout.excalidraw`](excalidraw/03_ocr_and_layout.excalidraw) |
| **04** | **Receipt Parsing & Financial Fields** | Nullable financial breakdown & spatial line item matching | **CURRENT** | [`mermaid/04_receipt_parsing.mmd`](mermaid/04_receipt_parsing.mmd) | [`excalidraw/04_receipt_parsing.excalidraw`](excalidraw/04_receipt_parsing.excalidraw) |
| **05** | **LLM & Vision Fallback Architecture** | Normal Text LLM path vs Vision AI fallback path | **CURRENT / FUTURE** | [`mermaid/05_llm_and_vision_fallback.mmd`](mermaid/05_llm_and_vision_fallback.mmd) | [`excalidraw/05_llm_and_vision_fallback.excalidraw`](excalidraw/05_llm_and_vision_fallback.excalidraw) |
| **06** | **Domain Model Entities** | Class diagram of domain models, validators & preprocessors | **CURRENT** | [`mermaid/06_domain_model.mmd`](mermaid/06_domain_model.mmd) | [`excalidraw/06_domain_model.excalidraw`](excalidraw/06_domain_model.excalidraw) |
| **07** | **Validation & Error Handling** | Exception handling, fallbacks, and schema validation rules | **CURRENT** | [`mermaid/07_validation_and_error_handling.mmd`](mermaid/07_validation_and_error_handling.mmd) | [`excalidraw/07_validation_and_error_handling.excalidraw`](excalidraw/07_validation_and_error_handling.excalidraw) |
| **08** | **Project Architecture & Layers** | Clean Architecture package layout & dependency flow | **CURRENT** | [`mermaid/08_project_architecture.mmd`](mermaid/08_project_architecture.mmd) | [`excalidraw/08_project_architecture.excalidraw`](excalidraw/08_project_architecture.excalidraw) |
| **09** | **End-to-End Sequence Diagram** | Execution sequence diagram for a receipt processing request | **CURRENT** | [`mermaid/09_end_to_end_sequence.mmd`](mermaid/09_end_to_end_sequence.mmd) | [`excalidraw/09_end_to_end_sequence.excalidraw`](excalidraw/09_end_to_end_sequence.excalidraw) |
| **10** | **Data Lifecycle & Transformations** | Data transformation pipeline from raw pixels to output JSON | **CURRENT** | [`mermaid/10_data_lifecycle.mmd`](mermaid/10_data_lifecycle.mmd) | [`excalidraw/10_data_lifecycle.excalidraw`](excalidraw/10_data_lifecycle.excalidraw) |
| **11** | **Benchmark Architecture** | Benchmark runner evaluating PaddleOCR vs PP-StructureV3 | **CURRENT** | [`mermaid/11_benchmark_architecture.mmd`](mermaid/11_benchmark_architecture.mmd) | [`excalidraw/11_benchmark_architecture.excalidraw`](excalidraw/11_benchmark_architecture.excalidraw) |
| **12** | **Test Architecture** | Automated test suite structure & synthetic data generators | **CURRENT** | [`mermaid/12_test_architecture.mmd`](mermaid/12_test_architecture.mmd) | [`excalidraw/12_test_architecture.excalidraw`](excalidraw/12_test_architecture.excalidraw) |
| **13** | **Configuration & Dependencies** | Config system, environment flags, and runtime dependencies | **CURRENT** | [`mermaid/13_configuration_and_dependencies.mmd`](mermaid/13_configuration_and_dependencies.mmd) | [`excalidraw/13_configuration_and_dependencies.excalidraw`](excalidraw/13_configuration_and_dependencies.excalidraw) |
| **14** | **Deployment & Runtime Topology** | Workstation OS, Python process, Paddle C++, and Ollama CLI | **CURRENT** | [`mermaid/14_deployment_runtime.mmd`](mermaid/14_deployment_runtime.mmd) | [`excalidraw/14_deployment_runtime.excalidraw`](excalidraw/14_deployment_runtime.excalidraw) |
| **15** | **Future Vision Pipeline Roadmap** | Planned FastAPI web service, SQLite store & Vision LLM | **PLANNED / FUTURE** | [`mermaid/15_future_vision_pipeline.mmd`](mermaid/15_future_vision_pipeline.mmd) | [`excalidraw/15_future_vision_pipeline.excalidraw`](excalidraw/15_future_vision_pipeline.excalidraw) |

---

## 2. How to Open & Edit Excalidraw Files

To open and visually edit any `.excalidraw` file:

1. Open **[Excalidraw](https://excalidraw.com/)** in your browser (or use the VS Code Excalidraw Extension).
2. Click **Menu** (top left hamburger icon) $\rightarrow$ **Open**.
3. Select any `.excalidraw` file from `docs/diagrams/excalidraw/`.
4. *Alternatively*, simply drag and drop the `.excalidraw` file directly into your browser window on Excalidraw.com!

---

## 3. Implementation Distinctions (Current vs Planned)

- **CURRENT Operational Pipeline:** Uses `PaddleOcrEngine` (`PP-OCRv5`), `SpatialLayoutParser` (deterministic layout geometry & RTL/LTR Arabic price matching), and `OllamaLlmClient` (`qwen2.5:3b` local text LLM) validated by `ReceiptValidator`.
- **PLANNED / FUTURE Extensions:** 
  - **Vision LLM Fallback (Diagram 05 & 15):** Multimodal fallback (e.g. Qwen2-VL or PaddleOCR-VL) for low-confidence images or severely corrupted layout tables.
  - **FastAPI Web Service & DB Storage (Diagram 15):** REST API endpoints and SQLite expense database persistency.
  - **PP-StructureV3 GPU Execution (Diagram 11 & 15):** Running PP-StructureV3 on CUDA GPU to bypass the CPU oneDNN PIR executor double-attribute conversion bug.
