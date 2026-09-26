"""HPA axis model — SPOF #12, #17 annihilated."""

from __future__ import annotations

import logging
import math

logger = logging.getLogger(__name__)


class HPAAxisModel:
    """Hypothalamic-Pituitary-Adrenal axis.

    Models the cortisol/DHEA cascade, allostatic load and the
    anabolic/catabolic ratio with a circadian phase.
    """

    def __init__(
        self,
        cortisol_8am: float = 15.0,
        cortisol_nadir: float = 3.0,
        dhea_s: float = 200.0,
        current_hour: float = 8.0,
    ) -> None:
        self.cortisol_8am = cortisol_8am
        self.cortisol_nadir = cortisol_nadir
        self.dhea_s = dhea_s
        self.hour = current_hour

    def calc_circadian_cortisol(self) -> float:
        """Cosine circadian cortisol model peaking at 8 AM."""
        phase = 2 * math.pi * (self.hour - 8) / 24
        amplitude = (self.cortisol_8am - self.cortisol_nadir) / 2
        midpoint = (self.cortisol_8am + self.cortisol_nadir) / 2
        return midpoint + amplitude * math.cos(phase)

    def calc_allostatic_load(self) -> float:
        """Cortisol/DHEA ratio as allostatic load index. Normal ~0.075."""
        current_cortisol = self.calc_circadian_cortisol()
        ratio = current_cortisol / max(1.0, self.dhea_s / 10)
        allostatic_index = ratio / 0.075

        if allostatic_index > 3.0:
            logger.warning(
                "Allostatic load=%.1f (normal=1.0). Catabolic dominance. "
                "Tissue repair suppressed. DHEA depleted.",
                allostatic_index,
            )
        elif allostatic_index > 1.5:
            logger.info("Allostatic load elevated (%.1f). Mild catabolic shift.", allostatic_index)

        return allostatic_index

    def calc_anabolic_catabolic_ratio(self) -> float:
        """DHEA (anabolic) vs cortisol (catabolic)."""
        current_cortisol = self.calc_circadian_cortisol()
        ratio = self.dhea_s / max(1.0, current_cortisol * 10)
        if ratio < 0.3:
            logger.warning("DHEA/Cortisol ratio=%.2f. Catabolic collapse.", ratio)
        return ratio

    def evaluate_adrenal_reserve(self) -> str:
        """Screen for adrenal strata rejections."""
        if self.cortisol_8am < 5.0:
            return (
                "[HPA-KILL] Cortisol 8AM < 5 μg/dL. Adrenal insufficiency. "
                "Stress-dose hydrocortisone required."
            )
        if self.dhea_s < 50:
            return "[HPA-WARN] DHEA-S critically low. Adrenal exhaustion. Immunosenescence active."
        return "STABLE"


__all__ = ["HPAAxisModel"]
