import math
from typing import List, Dict, Any, Optional
from .models import OcrElement


class LayoutCalculator:
    """Provides pure geometric distance and proximity spatial calculations for layout parsing."""

    @staticmethod
    def y_distance(item1: OcrElement, item2: OcrElement) -> float:
        return abs(item1.center_y - item2.center_y)

    @staticmethod
    def x_distance(item1: OcrElement, item2: OcrElement) -> float:
        return abs(item1.center_x - item2.center_x)

    @staticmethod
    def euclidean_distance(item1: OcrElement, item2: OcrElement) -> float:
        dx = item1.center_x - item2.center_x
        dy = item1.center_y - item2.center_y
        return math.hypot(dx, dy)

    @classmethod
    def find_closest_number_y(
        cls,
        item: OcrElement,
        candidate_numbers: List[OcrElement],
        max_y_distance: float = 20.0,
        used_ids: Optional[set] = None
    ) -> Optional[OcrElement]:
        if used_ids is None:
            used_ids = set()

        eligible = [
            num for num in candidate_numbers
            if id(num) not in used_ids and cls.y_distance(item, num) <= max_y_distance
        ]

        if not eligible:
            return None

        # Prioritize same-line Y distance first, then X distance
        return min(eligible, key=lambda num: (cls.y_distance(num, item), cls.x_distance(num, item)))
