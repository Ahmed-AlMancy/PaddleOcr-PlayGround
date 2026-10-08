from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple


@dataclass(frozen=True)
class BoundingBox:
    points: List[List[float]]

    @property
    def center_x(self) -> float:
        if not self.points:
            return 0.0
        return sum(pt[0] for pt in self.points) / len(self.points)

    @property
    def center_y(self) -> float:
        if not self.points:
            return 0.0
        return sum(pt[1] for pt in self.points) / len(self.points)


@dataclass
class OcrElement:
    text: str
    confidence: float
    box: List[List[float]] = field(default_factory=list)
    center_x: float = 0.0
    center_y: float = 0.0
    is_number: bool = False
    contains_arabic: bool = False


@dataclass
class ReceiptItem:
    original_ocr: str
    name: str
    price: Optional[float] = None
    category: str = "Other"
    correction_confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_ocr": self.original_ocr,
            "name": self.name,
            "price": round(self.price, 2) if self.price is not None else None,
            "category": self.category,
            "correction_confidence": round(self.correction_confidence, 4),
        }


@dataclass
class StructuredReceipt:
    merchant: Optional[str] = None
    receipt_number: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    currency: Optional[str] = None
    payment_method: Optional[str] = None
    items: List[ReceiptItem] = field(default_factory=list)
    subtotal: Optional[float] = None
    discount: Optional[float] = None
    service_charge: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "merchant": self.merchant,
            "receipt_number": self.receipt_number,
            "date": self.date,
            "time": self.time,
            "currency": self.currency,
            "payment_method": self.payment_method,
            "items": [item.to_dict() for item in self.items],
            "subtotal": self.subtotal,
            "discount": self.discount,
            "service_charge": self.service_charge,
            "tax": self.tax,
            "total": self.total,
        }
