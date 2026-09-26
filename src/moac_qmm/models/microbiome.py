"""Microbiome metabolizer — SPOF #7 annihilated."""

from __future__ import annotations

import logging
from typing import ClassVar

from moac_qmm.constants import MICROBIOME_DIVERSITY_FLOOR

logger = logging.getLogger(__name__)


class MicrobiomeMetabolizer:
    """Gut bacteria metabolize ~40% of oral drugs (kernel assumption)."""

    DRUG_MICROBIOME_INTERACTIONS: ClassVar[dict[str, list[str]]] = {
        "Levodopa": ["Enterococcus faecalis"],
        "Sulfasalazine": ["Bacteroides fragilis"],
        "Digoxin": ["Eggerthella lenta"],
        "Esomeprazole": ["Lactobacillus"],
    }

    def __init__(
        self, shannon_diversity: float = 3.5, pathobionts: list[str] | None = None
    ) -> None:
        self.diversity = shannon_diversity
        self.pathobionts = pathobionts or []

    def calc_bioavailability_modifier(self, drug_name: str, route: str) -> float:
        """Bioavailability derate from pathobiont drug metabolism."""
        if route != "oral":
            return 1.0
        if self.diversity < MICROBIOME_DIVERSITY_FLOOR:
            logger.warning("Shannon diversity=%.1f. Dysbiosis.", self.diversity)
        for drug, organisms in self.DRUG_MICROBIOME_INTERACTIONS.items():
            if drug_name == drug and any(o in self.pathobionts for o in organisms):
                logger.warning(
                    "%s metabolizes %s. Bioavailability collapses.",
                    organisms[0],
                    drug_name,
                )
                return 0.2
        return 1.0

    def calc_ppi_microbiome_shift(self, ppi_exposure_weeks: float) -> dict[str, float]:
        """v28: chronic PPI use alters microbiome composition."""
        if ppi_exposure_weeks > 4:
            logger.info(
                "PPI exposure=%.0f weeks. Gastric pH barrier weakened → oral "
                "bacteria translocate to gut.",
                ppi_exposure_weeks,
            )
            return {"diversity_penalty": 0.7, "sibo_risk": 1.5, "c_diff_risk": 2.0}
        return {"diversity_penalty": 1.0, "sibo_risk": 1.0, "c_diff_risk": 1.0}


__all__ = ["MicrobiomeMetabolizer"]
