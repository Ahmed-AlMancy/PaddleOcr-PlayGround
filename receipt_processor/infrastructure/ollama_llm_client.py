import json
import logging
import subprocess
from typing import Dict, Any, Optional
from ..contracts.llm_client import ILLMClient
from ..domain.models import StructuredReceipt
from ..domain.category_rules import ALLOWED_CATEGORIES
from ..config import get_ollama_path, get_ollama_model
from ..domain.validator import ReceiptValidator

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """You are a generic semantic expense receipt parser and classification system.
Your task is to analyze receipt items (in Arabic, English, or mixed languages), correct obvious OCR spelling mistakes conservatively, and categorize each item semantically.

ALLOWED TOP-LEVEL CATEGORIES:
{allowed_categories_list}

CRITICAL CATEGORY RULES:
1. Every item category MUST be EXACTLY ONE of the 16 ALLOWED TOP-LEVEL CATEGORIES listed above.
2. DO NOT invent sub-categories or synonyms (e.g. NEVER use 'Drinks', 'Snacks', 'Fruits', 'Dairy', 'Technology', 'Medical').
   - Fruits, vegetables, snacks, drinks, milk, grocery items -> 'Groceries' or 'Food'
   - Meals at restaurants/cafes -> 'Dining'
   - Phones, cables, electronics -> 'Electronics'
   - Medicine, pharmacy -> 'Health'
   - Taxis, fuel, travel tickets -> 'Transportation' or 'Travel'
3. DO NOT use hardcoded product dictionaries. Determine meaning dynamically from context.

LANGUAGE & ARABIC OCR CORRECTION RULES:
1. When input item has bilingual text (e.g. '1-Mutabel / عتبل'), normalize 'name' to the clear product name (e.g. 'متبل').
2. Correct obvious OCR typos based on standard Arabic vocabulary:
   - 'حعص' -> 'حمص'
   - 'عتبل' -> 'متبل'
   - 'سلطة خصراء' -> 'سلطة خضراء'
   - 'سلة حبز' -> 'سلة خبز'
   - 'تفادة' -> 'تفاحة'
3. Always keep 'original_ocr' exactly as provided in the input.
4. Keep the item 'price' unchanged from the input item.
5. Set 'correction_confidence' between 0.0 (very low confidence correction) and 1.0 (exact match or highly confident correction).

INPUT RECEIPT ITEMS:
{items_json}

OUTPUT FORMAT:
Return ONLY valid JSON matching this exact structure:
{{
  "items": [
    {{
      "original_ocr": "exact text from input",
      "name": "corrected product name",
      "price": 2.0,
      "category": "Groceries",
      "correction_confidence": 1.0
    }}
  ]
}}

Do not include any intro, markdown text, or explanations outside the JSON object.
"""


class OllamaLlmClient(ILLMClient):
    """Concrete Ollama implementation of ILLMClient contract."""

    def __init__(self, ollama_path: Optional[str] = None, timeout: int = 60):
        self.ollama_path = ollama_path or get_ollama_path()
        self.timeout = timeout

    @staticmethod
    def _extract_json(text: str) -> Optional[Dict[str, Any]]:
        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            return None

        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            return None

    def process_semantic_receipt(
        self,
        receipt: StructuredReceipt,
        model_name: Optional[str] = None
    ) -> StructuredReceipt:
        if not receipt.items:
            logger.warning("No items in receipt to process with LLM.")
            return receipt

        model = model_name or get_ollama_model()

        input_items = [
            {
                "original_ocr": item.original_ocr,
                "name": item.name,
                "price": item.price,
            }
            for item in receipt.items
        ]

        prompt = PROMPT_TEMPLATE.format(
            allowed_categories_list=", ".join(ALLOWED_CATEGORIES),
            items_json=json.dumps(input_items, ensure_ascii=False, indent=2)
        )

        logger.info(f"Invoking Ollama model '{model}' at '{self.ollama_path}'...")
        try:
            res = subprocess.run(
                [self.ollama_path, "run", model],
                input=prompt,
                text=True,
                capture_output=True,
                encoding="utf-8",
                timeout=self.timeout
            )

            if res.returncode != 0:
                logger.error(f"Ollama execution failed with returncode {res.returncode}: {res.stderr}")
                return receipt

            response_text = res.stdout
            logger.debug(f"Raw LLM response: {response_text}")

        except FileNotFoundError:
            logger.error(f"Ollama executable not found at '{self.ollama_path}'. Skipping LLM step.")
            return receipt
        except subprocess.TimeoutExpired:
            logger.error(f"Ollama execution timed out after {self.timeout} seconds. Skipping LLM step.")
            return receipt
        except Exception as e:
            logger.error(f"Unexpected error running Ollama: {e}")
            return receipt

        raw_json = self._extract_json(response_text)
        if not raw_json:
            logger.error("Could not extract valid JSON from LLM output. Keeping default categorization.")
            return receipt

        return ReceiptValidator.validate_receipt_dict(raw_json, original_receipt=receipt)
