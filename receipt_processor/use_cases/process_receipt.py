import json
import os
import logging
from typing import Dict, Any, Optional
from ..contracts.ocr_engine import IOCREngine
from ..contracts.llm_client import ILLMClient
from ..infrastructure.paddle_ocr_engine import PaddleOcrEngine
from ..infrastructure.json_ocr_loader import JsonOcrLoader
from ..infrastructure.ollama_llm_client import OllamaLlmClient
from ..domain.preprocessor import ReceiptPreprocessor
from .spatial_parser import SpatialLayoutParser
from ..domain.models import StructuredReceipt

logger = logging.getLogger(__name__)


class ProcessReceiptUseCase:
    """
    Main Application Use Case for processing receipts (Clean Architecture Orchestrator).
    Depends on contracts/abstractions (IOCREngine, ILLMClient) rather than concrete implementations (DIP).
    """

    def __init__(
        self,
        ocr_engine: Optional[IOCREngine] = None,
        json_loader: Optional[IOCREngine] = None,
        llm_client: Optional[ILLMClient] = None,
    ):
        self.ocr_engine = ocr_engine or PaddleOcrEngine()
        self.json_loader = json_loader or JsonOcrLoader()
        self.llm_client = llm_client or OllamaLlmClient()

    def execute(
        self,
        input_path: str,
        output_path: Optional[str] = "receipt_output.json",
        use_llm: bool = True,
        ocr_lang: str = "ar",
        ollama_model: Optional[str] = None
    ) -> Dict[str, Any]:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Step 1: Obtain raw OCR items via appropriate OCR engine contract
        if input_path.lower().endswith(".json"):
            raw_ocr_items = self.json_loader.extract_text(input_path, lang=ocr_lang)
        else:
            raw_ocr_items = self.ocr_engine.extract_text(input_path, lang=ocr_lang)

        if not raw_ocr_items:
            logger.warning(f"No OCR text detected in {input_path}")
            empty_dict = StructuredReceipt().to_dict()
            if output_path:
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(empty_dict, f, ensure_ascii=False, indent=2)
            return empty_dict

        # Step 2: Preprocess spatial coordinates & sort reading order
        prepared_ocr = ReceiptPreprocessor.prepare_ocr_elements(raw_ocr_items)

        # Step 3: Generic spatial layout parsing into StructuredReceipt entity
        parsed_receipt = SpatialLayoutParser.parse(prepared_ocr)

        # Step 4: Local LLM semantic correction & categorization via ILLMClient contract
        if use_llm:
            final_receipt_model = self.llm_client.process_semantic_receipt(
                parsed_receipt,
                model_name=ollama_model
            )
        else:
            final_receipt_model = parsed_receipt

        # Step 5: Convert domain entity to dictionary
        final_dict = final_receipt_model.to_dict()

        # Step 6: Save output artifact if requested
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(final_dict, f, ensure_ascii=False, indent=2)
            logger.info(f"Successfully saved structured output to {output_path}")

        return final_dict
