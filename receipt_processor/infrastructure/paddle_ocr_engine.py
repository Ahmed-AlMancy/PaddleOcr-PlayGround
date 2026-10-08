import os
import logging
from typing import List, Dict, Any
from ..contracts.ocr_engine import IOCREngine

logger = logging.getLogger(__name__)

_ocr_instances: Dict[str, Any] = {}


class PaddleOcrEngine(IOCREngine):
    """Concrete PaddleOCR implementation of IOCREngine contract."""

    def __init__(self, default_lang: str = "ar"):
        self.default_lang = default_lang

    def _get_engine(self, lang: str):
        global _ocr_instances
        if lang not in _ocr_instances:
            logger.info(f"Initializing PaddleOCR (lang='{lang}')...")
            from paddleocr import PaddleOCR
            _ocr_instances[lang] = PaddleOCR(
                lang=lang,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                enable_mkldnn=False,
            )
        return _ocr_instances[lang]

    def extract_text(self, input_path: str, lang: str = "ar") -> List[Dict[str, Any]]:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Receipt image file not found: {input_path}")

        use_lang = lang or self.default_lang
        logger.info(f"Running PaddleOCR (lang='{use_lang}') on image: {input_path}")
        ocr = self._get_engine(use_lang)
        results = ocr.predict(input_path)

        all_results = []
        if results:
            for result in results:
                texts = result.get("rec_texts", [])
                scores = result.get("rec_scores", [])
                boxes = result.get("rec_polys", [])

                for text, score, box in zip(texts, scores, boxes):
                    box_list = box.tolist() if hasattr(box, "tolist") else box
                    all_results.append({
                        "text": str(text),
                        "confidence": float(score),
                        "box": box_list
                    })

        return all_results
