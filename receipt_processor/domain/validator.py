import logging
from typing import Dict, Any, List, Optional
from .category_rules import CategoryValidator
from .models import StructuredReceipt, ReceiptItem

logger = logging.getLogger(__name__)


class ReceiptValidator:
    """Domain validator for enforcing receipt schema, price types, and category rules."""

    @staticmethod
    def validate_category(raw_category: Any) -> str:
        return CategoryValidator.validate_category(raw_category)

    @staticmethod
    def validate_confidence(raw_confidence: Any, default_val: float = 1.0) -> float:
        try:
            val = float(raw_confidence)
        except (ValueError, TypeError):
            val = default_val
        return max(0.0, min(1.0, val))

    @staticmethod
    def validate_price(raw_price: Any) -> Optional[float]:
        if raw_price is None:
            return None
        try:
            return float(raw_price)
        except (ValueError, TypeError):
            return None

    @classmethod
    def validate_item_dict(
        cls,
        raw_item: Dict[str, Any],
        original_ocr_fallback: str = "",
        fallback_price: Optional[float] = None
    ) -> Optional[ReceiptItem]:
        if not isinstance(raw_item, dict):
            return None

        original_ocr = raw_item.get("original_ocr")
        if not isinstance(original_ocr, str) or not original_ocr.strip():
            original_ocr = original_ocr_fallback or raw_item.get("name", "Unknown")

        name = raw_item.get("name")
        if not isinstance(name, str) or not name.strip():
            name = original_ocr

        price = fallback_price

        category = cls.validate_category(raw_item.get("category"))
        confidence = cls.validate_confidence(raw_item.get("correction_confidence"), default_val=1.0)

        return ReceiptItem(
            original_ocr=original_ocr,
            name=name,
            price=price,
            category=category,
            correction_confidence=confidence,
        )

    @classmethod
    def validate_receipt_dict(
        cls,
        raw_receipt: Dict[str, Any],
        original_receipt: Optional[StructuredReceipt] = None
    ) -> StructuredReceipt:
        validated = StructuredReceipt()

        if original_receipt:
            validated.merchant = original_receipt.merchant
            validated.receipt_number = original_receipt.receipt_number
            validated.date = original_receipt.date
            validated.time = original_receipt.time
            validated.currency = original_receipt.currency
            validated.subtotal = original_receipt.subtotal
            validated.discount = original_receipt.discount
            validated.service_charge = original_receipt.service_charge
            validated.tax = original_receipt.tax
            validated.total = original_receipt.total
            validated.payment_method = original_receipt.payment_method

        if isinstance(raw_receipt, dict):
            if "merchant" in raw_receipt and isinstance(raw_receipt["merchant"], str) and raw_receipt["merchant"].strip():
                validated.merchant = raw_receipt["merchant"]
            if "receipt_number" in raw_receipt and isinstance(raw_receipt["receipt_number"], str) and raw_receipt["receipt_number"].strip():
                validated.receipt_number = raw_receipt["receipt_number"]
            if "date" in raw_receipt and isinstance(raw_receipt["date"], str) and raw_receipt["date"].strip():
                validated.date = raw_receipt["date"]
            if "time" in raw_receipt and isinstance(raw_receipt["time"], str) and raw_receipt["time"].strip():
                validated.time = raw_receipt["time"]
            if "currency" in raw_receipt and isinstance(raw_receipt["currency"], str) and raw_receipt["currency"].strip():
                validated.currency = raw_receipt["currency"]
            if "payment_method" in raw_receipt and isinstance(raw_receipt["payment_method"], str) and raw_receipt["payment_method"].strip():
                validated.payment_method = raw_receipt["payment_method"]
            if "subtotal" in raw_receipt and raw_receipt["subtotal"] is not None:
                val = cls.validate_price(raw_receipt["subtotal"])
                if val is not None:
                    validated.subtotal = val
            if "discount" in raw_receipt and raw_receipt["discount"] is not None:
                val = cls.validate_price(raw_receipt["discount"])
                if val is not None:
                    validated.discount = val
            if "service_charge" in raw_receipt and raw_receipt["service_charge"] is not None:
                val = cls.validate_price(raw_receipt["service_charge"])
                if val is not None:
                    validated.service_charge = val
            if "tax" in raw_receipt and raw_receipt["tax"] is not None:
                val = cls.validate_price(raw_receipt["tax"])
                if val is not None:
                    validated.tax = val
            if "total" in raw_receipt and raw_receipt["total"] is not None:
                val = cls.validate_price(raw_receipt["total"])
                if val is not None:
                    validated.total = val

        raw_items = raw_receipt.get("items") if isinstance(raw_receipt, dict) else None
        if isinstance(raw_items, list):
            validated_items = []
            for idx, item_data in enumerate(raw_items):
                fallback_ocr = ""
                fallback_price = None
                if original_receipt and idx < len(original_receipt.items):
                    fallback_ocr = original_receipt.items[idx].original_ocr
                    fallback_price = original_receipt.items[idx].price
                
                valid_item = cls.validate_item_dict(
                    item_data,
                    original_ocr_fallback=fallback_ocr,
                    fallback_price=fallback_price
                )
                if valid_item:
                    validated_items.append(valid_item)
            validated.items = validated_items
        elif original_receipt:
            validated.items = original_receipt.items

        return validated
