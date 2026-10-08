import json
import os
import logging
from typing import List, Dict, Any
from ..contracts.ocr_engine import IOCREngine

logger = logging.getLogger(__name__)


class JsonOcrLoader(IOCREngine):
    """Concrete JSON file loader implementation of IOCREngine contract."""

    def extract_text(self, input_path: str, lang: str = "ar") -> List[Dict[str, Any]]:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"OCR JSON file not found: {input_path}")

        logger.info(f"Loading pre-computed OCR data from JSON: {input_path}")
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("OCR JSON file must contain a list of OCR items.")

        return data
