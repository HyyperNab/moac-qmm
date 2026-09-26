"""Hypoxia tensor — SPOF #6 annihilated."""

from __future__ import annotations

import logging

from moac_qmm.constants import HYPOXIA_CYP450_FLOOR, SPO2_NOMINAL
from moac_qmm.exceptions import HypoxiaCascade

logger = logging.getLogger(__name__)


class HypoxiaTensor:
    """Tissue O₂ affects CYP450, pathogen growth, and HIF-1α."""

    def __init__(self, spo2: float = 98.0, tissue_po2: float = 40.0) -> None:
        self.spo2 = spo2
        self.tissue_po2 = tissue_po2

    def calc_cyp450_derate(self) -> float:
        """CYP450 oxidative capacity as a function of SpO2; may kill."""
        if self.spo2 < HYPOXIA_CYP450_FLOOR:
            msg = (
                f"[HYPOXIA-KILL] SpO2={self.spo2:.1f}%. CYP450 dead. "
                f"All hepatic drugs enter toxic accumulation."
            )
            logger.critical(msg)
            raise HypoxiaCascade(msg)
        return max(0.1, (self.spo2 - HYPOXIA_CYP450_FLOOR) / (SPO2_NOMINAL - HYPOXIA_CYP450_FLOOR))

    def calc_pathogen_anaerobic_shift(self) -> float:
        """Anaerobic pathogen overgrowth multiplier in hypoxic tissue."""
        if self.tissue_po2 < 20:
            logger.info("Tissue pO2 < 20mmHg. Anaerobic pathogen overgrowth risk.")
            return 2.0
        return 1.0

    def calc_hif1alpha_restitution_boost(self) -> float:
        """HIF-1α driven restitution boost in the hypoxic sweet spot."""
        if 15 < self.tissue_po2 < 30:
            return 1.3  # HIF-1α sweet spot
        if self.tissue_po2 < 15:
            return 0.2  # too hypoxic → cell death
        return 1.0


__all__ = ["HypoxiaTensor"]
