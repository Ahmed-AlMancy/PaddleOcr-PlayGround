from abc import ABC, abstractmethod
from typing import Optional
from ..domain.models import StructuredReceipt


class ILLMClient(ABC):
    """Abstract contract for Large Language Model semantic classification clients (DIP / OCP)."""

    @abstractmethod
    def process_semantic_receipt(
        self,
        receipt: StructuredReceipt,
        model_name: Optional[str] = None
    ) -> StructuredReceipt:
        """Process structured receipt items for semantic correction and classification."""
        pass
