import re
import logging
from typing import List, Dict, Any, Optional
from ..domain.models import OcrElement, StructuredReceipt, ReceiptItem
from ..domain.preprocessor import ReceiptPreprocessor
from ..domain.layout_calculator import LayoutCalculator

logger = logging.getLogger(__name__)

RECEIPT_NO_LABELS = {
    "receipt no", "receipt #", "receipt number", "order number", "order no",
    "ticket no", "ticket #", "inv", "invoice no", "invoice #", "رقم الفاتورة", "رقم الطلب", "فاتورة رقم", "رقم الفاتوره"
}

SUBTOTAL_LABELS = {
    "subtotal", "sub-total", "sub total", "net subtotal", "price", "price:",
    "total item", "total items", "إجمالي العناصر", "مجموع العناصر", "المجموع الفرعي", "الفرعي"
}

NET_TOTAL_LABELS = {
    "net amount", "grand total", "net total", "amount due", "balance due", "total due",
    "صافي", "إجمالي الصافي", "الصافي", "النهائي", "النهائى", "الإجمالي النهائي", "الإجمالى النهائى",
    "الأجمالى بعد التقريب", "الاجمالي بعد التقريب", "الإجمالي بعد التقريب", "المبلغ المطلوب"
}

TOTAL_LABELS = {
    "total", "total amount", "total:", "المجموع", "الإجمالي", "إجمالي", "الجملة", "مجموع"
}

TAX_LABELS = {
    "tax", "tax:", "vat", "vat amount", "gst", "sales tax", "vat14%", "vat15%", "vat%",
    "ضريبة", "الضريبة", "ضريبة القيمة المضافة", "القيمة المضافة", "ضريية", "القبمه المضافه"
}

PAYMENT_CASH_WORDS = ["cash", "نقدا", "نقدى", "كاش", "استلم"]
PAYMENT_CARD_WORDS = ["credit", "debit", "card", "visa", "mastercard", "amex", "apple pay", "بطاقة", "شبكة", "فيزا"]

TABLE_HEADER_WORDS = {
    "item", "items", "qty", "quantity", "price", "unit price", "amount", "description",
    "total", "الوصف", "الصنف", "صنف", "الكمية", "الكميه", "السعر", "القيمة", "القيمه", "الإجمالي", "المجموع",
    "رصف", "الصلف", "وصف"
}

EXACT_CURRENCY_SYMBOLS = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "¥": "JPY",
}

WORD_CURRENCY_CODES = {
    "usd": "USD",
    "eur": "EUR",
    "gbp": "GBP",
    "egp": "EGP", "le": "EGP", "l.e": "EGP", "ج.م": "EGP", "جنيه": "EGP",
    "sar": "SAR", "sr": "SAR", "ريال": "SAR", "ر.س": "SAR",
    "aed": "AED", "درهم": "AED", "د.إ": "AED",
    "kwd": "KWD", "د.ك": "KWD",
}

SERVICE_LABELS = {
    "service", "service charge", "service:", "خدمة", "الخدمة", "رسوم الخدمة"
}

DISCOUNT_LABELS = {
    "discount", "discounts", "discount:", "saving", "savings", "وفرت", "الخصم", "الخصومات", "خصم"
}

EXCLUDED_ITEM_TEXTS = set.union(
    RECEIPT_NO_LABELS, SUBTOTAL_LABELS, NET_TOTAL_LABELS, TOTAL_LABELS, TAX_LABELS, SERVICE_LABELS, DISCOUNT_LABELS,
    {
        "your receipt", "thank you", "welcome", "شكرا لزيارتكم", "شكرا", "recieved", "change",
        "amount", "qty", "item name", "item", "items", "sale", "table", "description", "unit price",
        "total item", "total items", "صنف", "الصنف", "الوصف", "الكمية", "السعر", "عدد الأصناف", "عدد الاصناف",
        "كاش", "المتبقي", "متبقي", "الباقي", "وفرت", "الخصومات", "العروض", "اكتساب", "رصيدك", "للك",
        "المنتجات", "الشراء", "شروط", "سياسة", "الشركة", "الشركه", "س ت", "ب ض", "عميل"
    }
)


class SpatialLayoutParser:
    """Use Case / Domain service for spatial layout parsing into StructuredReceipt."""

    @staticmethod
    def detect_currency(text: str) -> Optional[str]:
        text_lower = text.lower()
        for symbol, code in EXACT_CURRENCY_SYMBOLS.items():
            if symbol in text:
                return code
        for word, code in WORD_CURRENCY_CODES.items():
            if re.search(rf"\b{re.escape(word)}\b", text_lower):
                return code
        return None

    @staticmethod
    def matches_label(text: str, label_set: set) -> bool:
        lower = text.strip().lower()
        if lower in label_set:
            return True
        return any(re.search(rf"\b{re.escape(lbl)}\b", lower) for lbl in label_set)

    @classmethod
    def detect_table_header_y(cls, prepared_ocr: List[OcrElement]) -> Optional[float]:
        """Detect Y coordinate of table header row (e.g. Item Qty Price Total / وصف الصنف الكمية السعر القيمة)."""
        lines: Dict[int, List[OcrElement]] = {}
        for item in prepared_ocr:
            y_bucket = int(item.center_y // 15)
            lines.setdefault(y_bucket, []).append(item)

        for bucket, items in lines.items():
            words_in_line = [it.text.strip().lower() for it in items]
            matched_words = [w for w in words_in_line if any(hw in w for hw in TABLE_HEADER_WORDS)]
            
            # Count distinct header terms matched across line elements or within single merged text block
            merged_text = " ".join(words_in_line)
            matched_single = [hw for hw in TABLE_HEADER_WORDS if hw in merged_text]

            if len(matched_words) >= 2 or len(matched_single) >= 2:
                return sum(it.center_y for it in items) / len(items)

        return None

    @classmethod
    def extract_merchant_name(cls, prepared_ocr: List[OcrElement], table_header_y: Optional[float] = None) -> Optional[str]:
        first_meta_y = float("inf")
        if table_header_y is not None:
            first_meta_y = min(first_meta_y, table_header_y)

        for item in prepared_ocr:
            txt = item.text.strip()
            if cls.matches_label(txt, RECEIPT_NO_LABELS) or "date:" in txt.lower() or "time:" in txt.lower() or "table:" in txt.lower() or "عميل" in txt:
                first_meta_y = min(first_meta_y, item.center_y)

        top_limit = min(first_meta_y, 250.0)
        top_text_items = [
            item for item in prepared_ocr
            if not item.is_number and item.center_y < top_limit
        ]

        if not top_text_items:
            return None

        top_text_items.sort(key=lambda x: (x.center_y, x.center_x))
        top_y = top_text_items[0].center_y
        header_items = [item for item in top_text_items if abs(item.center_y - top_y) <= 30.0]
        header_words = [item.text.strip() for item in header_items]
        filtered = [w for w in header_words if w.lower() not in {"your receipt", "welcome", "invoice"}]
        if filtered:
            return " ".join(filtered)
        return None

    @classmethod
    def parse(cls, prepared_ocr: List[OcrElement]) -> StructuredReceipt:
        numbers = [item for item in prepared_ocr if item.is_number]
        text_items = [item for item in prepared_ocr if not item.is_number]

        table_header_y = cls.detect_table_header_y(prepared_ocr)

        receipt = StructuredReceipt()
        receipt.merchant = cls.extract_merchant_name(prepared_ocr, table_header_y=table_header_y)

        # 1. Metadata & Summary Totals extraction
        for item in prepared_ocr:
            text_clean = item.text.strip()
            lower = text_clean.lower()

            # Skip table header row labels when parsing summary totals
            if table_header_y is not None and abs(item.center_y - table_header_y) <= 15:
                continue

            if not receipt.currency:
                found_curr = cls.detect_currency(text_clean)
                if found_curr:
                    receipt.currency = found_curr

            if cls.matches_label(text_clean, RECEIPT_NO_LABELS):
                candidates = [n for n in numbers if abs(n.center_y - item.center_y) <= 25]
                if candidates:
                    closest = min(candidates, key=lambda n: (LayoutCalculator.y_distance(n, item), LayoutCalculator.x_distance(n, item)))
                    receipt.receipt_number = closest.text

            elif cls.matches_label(text_clean, SUBTOTAL_LABELS):
                candidates = [n for n in numbers if abs(n.center_y - item.center_y) <= 20 or item.center_y < n.center_y < item.center_y + 35]
                if candidates:
                    closest = min(candidates, key=lambda n: (LayoutCalculator.y_distance(n, item), LayoutCalculator.x_distance(n, item)))
                    val = ReceiptPreprocessor.parse_number_value(closest.text)
                    if val is not None:
                        receipt.subtotal = val

            elif cls.matches_label(text_clean, SERVICE_LABELS):
                candidates = [n for n in numbers if abs(n.center_y - item.center_y) <= 20]
                if candidates:
                    closest = min(candidates, key=lambda n: (LayoutCalculator.y_distance(n, item), LayoutCalculator.x_distance(n, item)))
                    val = ReceiptPreprocessor.parse_number_value(closest.text)
                    if val is not None:
                        receipt.service_charge = val

            elif cls.matches_label(text_clean, DISCOUNT_LABELS):
                candidates = [n for n in numbers if abs(n.center_y - item.center_y) <= 20]
                if candidates:
                    closest = min(candidates, key=lambda n: (LayoutCalculator.y_distance(n, item), LayoutCalculator.x_distance(n, item)))
                    val = ReceiptPreprocessor.parse_number_value(closest.text)
                    if val is not None:
                        receipt.discount = val

            elif cls.matches_label(text_clean, TAX_LABELS):
                candidates = [n for n in numbers if abs(n.center_y - item.center_y) <= 20]
                if candidates:
                    closest = min(candidates, key=lambda n: (LayoutCalculator.y_distance(n, item), LayoutCalculator.x_distance(n, item)))
                    val = ReceiptPreprocessor.parse_number_value(closest.text)
                    if val is not None:
                        receipt.tax = val

            elif cls.matches_label(text_clean, NET_TOTAL_LABELS):
                candidates = [n for n in numbers if abs(n.center_y - item.center_y) <= 20 or item.center_y - 10 <= n.center_y < item.center_y + 40]
                if candidates:
                    closest = min(candidates, key=lambda n: (LayoutCalculator.y_distance(n, item), LayoutCalculator.x_distance(n, item)))
                    val = ReceiptPreprocessor.parse_number_value(closest.text)
                    if val is not None:
                        receipt.total = val

            elif cls.matches_label(text_clean, TOTAL_LABELS) and not receipt.total:
                candidates = [n for n in numbers if abs(n.center_y - item.center_y) <= 20 or item.center_y - 10 <= n.center_y < item.center_y + 40]
                if candidates:
                    closest = min(candidates, key=lambda n: (LayoutCalculator.y_distance(n, item), LayoutCalculator.x_distance(n, item)))
                    val = ReceiptPreprocessor.parse_number_value(closest.text)
                    if val is not None:
                        if receipt.subtotal is None:
                            receipt.subtotal = val
                        else:
                            receipt.total = val

            if any(w in lower for w in PAYMENT_CASH_WORDS) and not receipt.payment_method:
                receipt.payment_method = "CASH"
            elif any(w in lower for w in PAYMENT_CARD_WORDS) and not receipt.payment_method:
                receipt.payment_method = "CARD"

        # 2. Date and Time extraction
        for item in prepared_ocr:
            text = item.text
            dt_match = re.search(r"(\d{1,2}:\d{2,4}(?::\d{2})?(?:\s*[AP]M)?)\s+(\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2})", text, re.IGNORECASE)
            if dt_match:
                receipt.time = dt_match.group(1)
                receipt.date = dt_match.group(2)
                continue

            dt_match2 = re.search(r"(\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2})\s+(\d{1,2}:\d{2,4}(?::\d{2})?(?:\s*[AP]M)?)", text, re.IGNORECASE)
            if dt_match2:
                receipt.date = dt_match2.group(1)
                receipt.time = dt_match2.group(2)
                continue

            if not receipt.date:
                d_match = re.search(r"(?:date:?\s*)?\b(\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2})\b", text, re.IGNORECASE)
                if d_match:
                    receipt.date = d_match.group(1)

            if not receipt.time:
                t_match = re.search(r"(?:time:?\s*)?\b(\d{1,2}:\d{2,4}(?::\d{2})?(?:\s*[AP]M)?)\b", text, re.IGNORECASE)
                if t_match:
                    receipt.time = t_match.group(1)

        # 3. Item identification & spatial bounds
        subtotal_y = None
        total_y = None
        for item in prepared_ocr:
            txt_clean = item.text.strip()
            if table_header_y is not None and abs(item.center_y - table_header_y) <= 15:
                continue

            if cls.matches_label(txt_clean, SUBTOTAL_LABELS) and subtotal_y is None:
                subtotal_y = item.center_y
            if (cls.matches_label(txt_clean, TOTAL_LABELS) or cls.matches_label(txt_clean, NET_TOTAL_LABELS)) and total_y is None:
                total_y = item.center_y

        if table_header_y is not None:
            min_y = table_header_y + 10.0
        else:
            min_y = 100.0 if any(it.center_y > 100 for it in prepared_ocr) else 0.0

        cutoff_y = subtotal_y or total_y or float("inf")

        raw_names = []
        for item in text_items:
            txt = item.text.strip()
            txt_lower = txt.lower()
            if min_y < item.center_y < cutoff_y:
                if not cls.matches_label(txt, EXCLUDED_ITEM_TEXTS) and not txt_lower.startswith("clerk:") and not txt_lower.startswith("machno:"):
                    raw_names.append(item)

        merged_names: List[OcrElement] = []
        used_name_ids = set()

        for item in raw_names:
            if id(item) in used_name_ids:
                continue

            same_line_partners = [
                p for p in raw_names
                if id(p) != id(item) and id(p) not in used_name_ids and abs(p.center_y - item.center_y) <= 15
            ]

            if same_line_partners:
                all_line_items = [item] + same_line_partners
                all_line_items.sort(key=lambda x: x.center_x)
                for p in all_line_items:
                    used_name_ids.add(id(p))

                combined_text = " / ".join(p.text.strip() for p in all_line_items)
                merged_names.append(OcrElement(
                    text=combined_text,
                    confidence=min(p.confidence for p in all_line_items),
                    center_x=sum(p.center_x for p in all_line_items) / len(all_line_items),
                    center_y=sum(p.center_y for p in all_line_items) / len(all_line_items),
                ))
            else:
                used_name_ids.add(id(item))
                merged_names.append(item)

        possible_prices = [item for item in numbers if min_y < item.center_y < cutoff_y]

        used_numbers = set()
        matched_items: List[ReceiptItem] = []

        for name_item in merged_names:
            clean_name = ReceiptPreprocessor.strip_quantity_prefix(name_item.text)
            if not clean_name or len(clean_name) <= 1:
                continue

            # Find all numbers on the same line (y_distance <= 18)
            same_line_numbers = [
                num for num in possible_prices
                if id(num) not in used_numbers and abs(num.center_y - name_item.center_y) <= 18.0
            ]

            price_val = None
            if same_line_numbers:
                # Filter for price formatted numbers (contains '.' or ',' or currency or float)
                price_candidates = [
                    num for num in same_line_numbers
                    if "." in num.text or "," in num.text or any(c in num.text for c in "$€£¥")
                ]

                # Fallback to all numbers on the line if no decimal number found
                chosen_candidates = price_candidates if price_candidates else same_line_numbers

                # RTL vs LTR price column selection:
                # In RTL Arabic tables, Item Name is on the right, Line Total Price is on the far LEFT (min center_x).
                # In LTR English tables, Item Name is on the left, Line Total Price is on the far RIGHT (max center_x).
                is_rtl = name_item.center_x > 350.0 or ReceiptPreprocessor.contains_arabic(name_item.text)
                if is_rtl:
                    chosen = min(chosen_candidates, key=lambda n: n.center_x)
                else:
                    chosen = max(chosen_candidates, key=lambda n: n.center_x)

                val = ReceiptPreprocessor.parse_number_value(chosen.text)
                if val is not None:
                    price_val = val

                # Mark all same line numbers as used
                for num in same_line_numbers:
                    used_numbers.add(id(num))

            matched_items.append(ReceiptItem(
                original_ocr=name_item.text,
                name=clean_name,
                price=price_val,
                category="Other",
                correction_confidence=float(name_item.confidence)
            ))

        receipt.items = matched_items
        return receipt
