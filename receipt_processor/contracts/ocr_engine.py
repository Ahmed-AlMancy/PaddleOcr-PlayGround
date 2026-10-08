from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IOCREngine(ABC):
    """Abstract contract for Optical Character Recognition engines (DIP / OCP)."""

    @abstractmethod
    def extract_text(self, input_path: str, lang: str = "ar") -> List[Dict[str, Any]]:
        """Extract text elements and bounding box coordinates from input file."""
        pass
