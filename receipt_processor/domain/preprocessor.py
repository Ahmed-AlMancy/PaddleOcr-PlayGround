import re
from typing import List, Dict, Any, Optional
from .models import OcrElement, BoundingBox

ARABIC_DIGITS_MAP = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")

KNOWN_CURRENCIES = {
    "$", "€", "£", "¥", "usd", "eur", "gbp", "egp", "le", "l.e", "ج.م", "جنيه",
    "sar", "sr", "ريال", "ر.س", "aed", "درهم", "د.إ", "kwd", "د.ك"
}


class ReceiptPreprocessor:
    """Domain preprocessor for text enrichment, digit translation, and price extraction."""

    @staticmethod
    def normalize_digits(text: str) -> str:
        return text.translate(ARABIC_DIGITS_MAP)

    @classmethod
    def clean_price_str(cls, text: str) -> str:
        text_clean = cls.normalize_digits(text).strip()

        # Ignore standalone quantity prefixes like "1-", "-1", "1x"
        if re.fullmatch(r"-?\d+[-xX]?", text_clean) or re.fullmatch(r"[-xX]?\d+", text_clean):
            return ""

        # Reject serial numbers, barcodes, or tax registration IDs (multiple hyphens or >= 7 digits without decimals)
        if re.search(r"\d+-\d+-\d+", text_clean):
            return ""
        if "." not in text_clean and "," not in text_clean and re.search(r"\b\d{6,}\b", text_clean):
            return ""

        # Support numbers with trailing OCR currency/letter artifacts like "17.0C", "14.5C", "15.0C"
        end_suffix_match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*[a-zA-Z\u0600-\u06FF]{1,3}", text_clean)
        if end_suffix_match:
            return end_suffix_match.group(1)

        words = re.findall(r"[a-zA-Z\u0600-\u06FF]+", text_clean)
        non_currency_words = [w for w in words if w.lower() not in KNOWN_CURRENCIES]

        if non_currency_words:
            return ""

        cleaned = re.sub(r"[^\d.,]", "", text_clean)
        return cleaned

    @classmethod
    def parse_number_value(cls, text: str) -> Optional[float]:
        cleaned = cls.clean_price_str(text)
        if not cleaned:
            return None

        if "," in cleaned and "." not in cleaned:
            if re.fullmatch(r"\d+,\d{1,2}", cleaned):
                cleaned = cleaned.replace(",", ".")
            else:
                cleaned = cleaned.replace(",", "")
        else:
            cleaned = cleaned.replace(",", "")

        try:
            return float(cleaned)
        except ValueError:
            return None

    @classmethod
    def is_number(cls, text: str) -> bool:
        text_clean = text.strip()
        if len(text_clean) > 20:
            return False
        return cls.parse_number_value(text_clean) is not None

    @staticmethod
    def strip_quantity_prefix(text: str) -> str:
        cleaned = re.sub(r"^/\s*[xX]\s*/\s*", "", text.strip())
        cleaned = re.sub(r"^[\s/\\\-–—xX]+", "", cleaned)
        cleaned = re.sub(r"^\d+(?:\.\d+)?\s*(?:kg|g|lb|lbs|kilo|كجم|جم|جرام|كيلو)?[\s\-–—xX/]+", "", cleaned.strip(), flags=re.IGNORECASE)
        cleaned = re.sub(r"^[-–—]?\d+(?:\.\d+)?[\s\-–—xX/]+", "", cleaned.strip())
        cleaned = re.sub(r"^\d+[-–—]", "", cleaned)
        cleaned = re.sub(r"[\s/\\-]+(?:\d+|[a-zA-Z])\s*$", "", cleaned)
        cleaned = re.sub(r"^[\s/\\\-–—xX]+", "", cleaned)
        return cleaned.strip()

    @staticmethod
    def contains_arabic(text: str) -> bool:
        return bool(re.search(r"[\u0600-\u06FF]", text))

    @classmethod
    def prepare_ocr_elements(cls, raw_ocr_items: List[Dict[str, Any]]) -> List[OcrElement]:
        prepared = []
        for item in raw_ocr_items:
            text = str(item.get("text", "")).strip()
            if not text:
                continue

            confidence = float(item.get("confidence", 0.0))
            box = item.get("box", [])
            bbox = BoundingBox(points=box)

            prepared.append(OcrElement(
                text=text,
                confidence=round(confidence, 4),
                box=box,
                center_x=round(bbox.center_x, 2),
                center_y=round(bbox.center_y, 2),
                is_number=cls.is_number(text),
                contains_arabic=cls.contains_arabic(text),
            ))

        prepared.sort(key=lambda x: (x.center_y, x.center_x))
        return prepared
