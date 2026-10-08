import pytest
from receipt_processor.domain.category_rules import ALLOWED_CATEGORIES, CategoryValidator
from receipt_processor.domain.validator import ReceiptValidator
from receipt_processor.domain.preprocessor import ReceiptPreprocessor
from receipt_processor.use_cases.spatial_parser import SpatialLayoutParser
from receipt_processor.infrastructure.ollama_llm_client import OllamaLlmClient
from receipt_processor.domain.models import StructuredReceipt, ReceiptItem


def create_synthetic_ocr_data(items_with_prices, currency_symbol="$"):
    """Helper to generate synthetic OCR boxes for item name and price pairs."""
    ocr_list = []
    y_pos = 120.0
    for name, price in items_with_prices:
        # Item name box (left side)
        ocr_list.append({
            "text": name,
            "confidence": 0.95,
            "box": [[50.0, y_pos - 10.0], [200.0, y_pos - 10.0], [200.0, y_pos + 10.0], [50.0, y_pos + 10.0]]
        })
        # Price box (right side, same Y)
        ocr_list.append({
            "text": f"{currency_symbol}{price:.2f}",
            "confidence": 0.99,
            "box": [[300.0, y_pos - 10.0], [380.0, y_pos - 10.0], [380.0, y_pos + 10.0], [300.0, y_pos + 10.0]]
        })
        y_pos += 30.0

    # Add subtotal footer to close receipt
    ocr_list.append({
        "text": "Subtotal",
        "confidence": 0.99,
        "box": [[50.0, y_pos - 10.0], [150.0, y_pos - 10.0], [150.0, y_pos + 10.0], [50.0, y_pos + 10.0]]
    })
    total_val = sum(p for _, p in items_with_prices)
    ocr_list.append({
        "text": f"{currency_symbol}{total_val:.2f}",
        "confidence": 0.99,
        "box": [[300.0, y_pos - 10.0], [380.0, y_pos - 10.0], [380.0, y_pos + 10.0], [300.0, y_pos + 10.0]]
    })

    return ocr_list


# =====================================================================
# 1. CATEGORY VALIDATION TESTS
# =====================================================================

def test_category_validation_allowed_categories():
    """Test that all exact allowed categories validate cleanly."""
    for cat in ALLOWED_CATEGORIES:
        assert CategoryValidator.validate_category(cat) == cat

def test_category_validation_case_insensitivity():
    """Test case-insensitive matching for allowed categories."""
    assert CategoryValidator.validate_category("groceries") == "Groceries"
    assert CategoryValidator.validate_category("FOOD") == "Food"
    assert CategoryValidator.validate_category("electronics") == "Electronics"

def test_category_validation_disallowed_categories():
    """Test that invalid/invented LLM categories fallback to 'Other' safely."""
    disallowed = ["Water", "Technology", "Medical", "Restaurant", "Beverages", "RandomCategory123"]
    for cat in disallowed:
        assert CategoryValidator.validate_category(cat) == "Other"


# =====================================================================
# 2. MALFORMED JSON & INVALID INPUT TESTS
# =====================================================================

def test_extract_json_from_markdown():
    """Test extracting JSON from LLM response wrapped in markdown code blocks."""
    raw_response = "Here is the parsed JSON:\n```json\n{\n  \"items\": []\n}\n```"
    res = OllamaLlmClient._extract_json(raw_response)
    assert res == {"items": []}

def test_extract_json_malformed():
    """Test handling malformed invalid JSON strings."""
    assert OllamaLlmClient._extract_json("Not a json string at all") is None
    assert OllamaLlmClient._extract_json("{ invalid json key: ") is None


# =====================================================================
# 3. ENGLISH NUMBERS & CURRENCY PARSING TESTS
# =====================================================================

def test_number_parsing_english_and_arabic_digits():
    """Test parsing prices with $, EGP, SAR, and Eastern Arabic digits."""
    assert ReceiptPreprocessor.parse_number_value("$12.99") == 12.99
    assert ReceiptPreprocessor.parse_number_value("12.99 USD") == 12.99
    assert ReceiptPreprocessor.parse_number_value("EGP 150.50") == 150.50
    assert ReceiptPreprocessor.parse_number_value("١٢.٩٩") == 12.99
    assert ReceiptPreprocessor.parse_number_value("٢٥٠.٠٠") == 250.00
    assert ReceiptPreprocessor.parse_number_value("SAR 50") == 50.0


# =====================================================================
# 4. PURE ENGLISH RECEIPT PARSING TEST
# =====================================================================

def test_pure_english_receipt():
    items = [
        ("Wireless Headphones", 79.99),
        ("Coffee Beans", 14.50),
        ("Running Shoes", 120.00)
    ]
    ocr_data = create_synthetic_ocr_data(items, currency_symbol="$")
    prepared = ReceiptPreprocessor.prepare_ocr_elements(ocr_data)
    receipt = SpatialLayoutParser.parse(prepared)
    
    assert receipt.currency == "USD"
    assert len(receipt.items) == 3
    assert receipt.items[0].original_ocr == "Wireless Headphones"
    assert receipt.items[0].price == 79.99
    assert receipt.items[1].original_ocr == "Coffee Beans"
    assert receipt.items[1].price == 14.50
    assert receipt.items[2].original_ocr == "Running Shoes"
    assert receipt.items[2].price == 120.00

    llm_client = OllamaLlmClient()
    res = llm_client.process_semantic_receipt(receipt)
    for item in res.items:
        assert item.category in ALLOWED_CATEGORIES
        assert isinstance(item.price, float)
        assert item.price > 0.0


# =====================================================================
# 5. DOMAIN SYNTHETIC RECEIPT PARSING & LLM CATEGORIZATION TESTS
# =====================================================================

def test_domain_a_arabic_food():
    items = [
        ("مياه معدنية", 2.00),
        ("شطيرة", 5.00),
        ("موز", 88.00),
        ("تفاحة", 111.00),
        ("حليب", 222.00)
    ]
    ocr_data = create_synthetic_ocr_data(items, currency_symbol="")
    prepared = ReceiptPreprocessor.prepare_ocr_elements(ocr_data)
    receipt = SpatialLayoutParser.parse(prepared)
    
    assert len(receipt.items) == 5
    for idx, (orig_name, orig_price) in enumerate(items):
        assert receipt.items[idx].original_ocr == orig_name
        assert receipt.items[idx].price == orig_price

    llm_client = OllamaLlmClient()
    res = llm_client.process_semantic_receipt(receipt)
    for item in res.items:
        assert item.category in ALLOWED_CATEGORIES
        assert isinstance(item.price, float)

def test_domain_b_clothing():
    items = [("قميص", 150.00), ("بنطلون", 250.00), ("حذاء", 300.00)]
    ocr_data = create_synthetic_ocr_data(items, currency_symbol="")
    prepared = ReceiptPreprocessor.prepare_ocr_elements(ocr_data)
    receipt = SpatialLayoutParser.parse(prepared)
    llm_client = OllamaLlmClient()
    res = llm_client.process_semantic_receipt(receipt)
    
    assert len(res.items) == 3
    for item in res.items:
        assert item.category in ALLOWED_CATEGORIES

def test_domain_c_electronics():
    items = [("Samsung Galaxy Charger", 120.00), ("Wireless Mouse", 45.00)]
    ocr_data = create_synthetic_ocr_data(items, currency_symbol="$")
    prepared = ReceiptPreprocessor.prepare_ocr_elements(ocr_data)
    receipt = SpatialLayoutParser.parse(prepared)
    llm_client = OllamaLlmClient()
    res = llm_client.process_semantic_receipt(receipt)
    
    assert len(res.items) == 2
    for item in res.items:
        assert item.category in ALLOWED_CATEGORIES

def test_domain_g_mixed_arabic_english():
    items = [("Samsung Charger", 120.00), ("قميص", 180.00), ("Milk", 35.00), ("Taxi", 50.00)]
    ocr_data = create_synthetic_ocr_data(items, currency_symbol="")
    prepared = ReceiptPreprocessor.prepare_ocr_elements(ocr_data)
    receipt = SpatialLayoutParser.parse(prepared)
    llm_client = OllamaLlmClient()
    res = llm_client.process_semantic_receipt(receipt)
    
    assert len(res.items) == 4
    for item in res.items:
        assert item.category in ALLOWED_CATEGORIES
        assert item.original_ocr in ["Samsung Charger", "قميص", "Milk", "Taxi"]
