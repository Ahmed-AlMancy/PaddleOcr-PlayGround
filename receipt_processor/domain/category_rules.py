import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

ALLOWED_CATEGORIES: List[str] = [
    "Food",
    "Groceries",
    "Dining",
    "Clothing",
    "Electronics",
    "Health",
    "Transportation",
    "Housing",
    "Utilities",
    "Entertainment",
    "Shopping",
    "Travel",
    "Education",
    "Personal Care",
    "Services",
    "Other",
]

CATEGORY_CASE_MAP: Dict[str, str] = {cat.lower(): cat for cat in ALLOWED_CATEGORIES}


class CategoryValidator:
    """Encapsulates validation and case-normalization rules for expense categories."""

    @staticmethod
    def validate_category(raw_category: Any) -> str:
        if not isinstance(raw_category, str):
            return "Other"

        cleaned = raw_category.strip()
        if cleaned in ALLOWED_CATEGORIES:
            return cleaned

        lower = cleaned.lower()
        if lower in CATEGORY_CASE_MAP:
            return CATEGORY_CASE_MAP[lower]

        logger.warning(f"Invalid category '{raw_category}' returned by LLM. Falling back to 'Other'.")
        return "Other"
