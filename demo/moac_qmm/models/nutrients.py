"""Nutrient substrate matrix — SPOF #8 annihilated.

Epithelial restitution requires building blocks. Liebig's Law of the
Minimum: the scarcest substrate caps restitution capacity.
"""

from __future__ import annotations

import logging
from typing import ClassVar

logger = logging.getLogger(__name__)


class NutrientSubstrateMatrix:
    """Daily substrate requirements for epithelial restitution."""

    REQUIRED_SUBSTRATES: ClassVar[dict[str, float]] = {
        "glutamine": 0.5,  # g/day
        "zinc": 8.0,  # mg/day
        "vitamin_c": 75.0,  # mg/day
        "vitamin_a": 900.0,  # µg/day
        "arginine": 4.0,  # g/day
        "n3_index": 8.0,  # % EPA+DHA
    }

    def __init__(self, serum_levels: dict[str, float]) -> None:
        self.levels = serum_levels

    def calc_restitution_capacity(self) -> float:
        """Minimum substrate ratio across all required substrates."""
        capacities: list[float] = []
        for nutrient, requirement in self.REQUIRED_SUBSTRATES.items():
            level = self.levels.get(nutrient, 0)
            ratio = level / requirement
            capacities.append(min(1.0, ratio))
            if ratio < 0.5:
                logger.warning(
                    "%s at %.1f/%.1f. Restitution impossible without substrate.",
                    nutrient,
                    level,
                    requirement,
                )
        return min(capacities) if capacities else 0.0


__all__ = ["NutrientSubstrateMatrix"]
