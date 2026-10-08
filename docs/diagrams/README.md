# Receipt Processing Pipeline System Architecture Diagrams

This directory contains the core system architecture documentation for the **Bilingual (Arabic/English) Receipt Expense Processing Pipeline**.

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

---

## 2. How to Open & Edit Excalidraw Files

To open and visually edit any `.excalidraw` file:

1. Open **[Excalidraw](https://excalidraw.com/)** in your browser (or use the VS Code Excalidraw Extension).
2. Click **Menu** (top left hamburger icon) -> **Open**.
3. Select any `.excalidraw` file from `docs/diagrams/excalidraw/`.
4. *Alternatively*, simply drag and drop the `.excalidraw` file directly into your browser window on Excalidraw.com!
