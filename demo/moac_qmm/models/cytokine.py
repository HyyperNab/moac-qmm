"""Cytokine storm vector — SPOF #14 annihilated.

Models IL-6 / TNF-α / IL-1β / IL-10 feedback loops over time.
"""

from __future__ import annotations

import logging

from moac_qmm.constants import IL6_STORM_THRESHOLD, TNF_ALPHA_LETHAL
from moac_qmm.exceptions import CytokineStormDetected

logger = logging.getLogger(__name__)


class CytokineStormVector:
    """First-order cytokine ODE with vagal and cortisol modulation."""

    def __init__(self) -> None:
        self.il6 = 7.0
        self.tnf_alpha = 5.0
        self.il1_beta = 1.0
        self.il10 = 2.0
        self.history: list[dict[str, float]] = []

    def step(
        self,
        pathogen_vector: float,
        immune_v: float,  # noqa: ARG002 — retained for API parity with v28
        hours: float = 1.0,
        vagal_suppression: float = 1.0,
        cortisol_level: float = 15.0,
    ) -> dict[str, float]:
        """Advance the cytokine system by ``hours``; may raise a storm kill."""
        cortisol_factor = max(0.3, 1.0 - (cortisol_level / 50.0) * 0.5)

        il6_production = 2.5 * max(0, pathogen_vector) * cortisol_factor + 0.3 * self.il6
        il6_clearance = 0.15 * self.il6

        tnf_production = (
            4.0 * max(0, pathogen_vector) * vagal_suppression * cortisol_factor
            + 0.1 * self.tnf_alpha
        )
        tnf_clearance = 0.4 * self.tnf_alpha

        il1_production = 1.0 * max(0, pathogen_vector) * cortisol_factor + 0.2 * self.il1_beta
        il1_clearance = 0.1 * self.il1_beta

        il10_production = 0.5 * max(0, self.il6 - 10) + 0.1 * self.il10
        il10_clearance = 0.05 * self.il10

        self.il6 = max(0, self.il6 + (il6_production - il6_clearance) * hours)
        self.tnf_alpha = max(0, self.tnf_alpha + (tnf_production - tnf_clearance) * hours)
        self.il1_beta = max(0, self.il1_beta + (il1_production - il1_clearance) * hours)
        self.il10 = max(0, self.il10 + (il10_production - il10_clearance) * hours)

        self.history.append(
            {
                "hour": float(len(self.history)),
                "IL-6": self.il6,
                "TNF-α": self.tnf_alpha,
                "IL-1β": self.il1_beta,
                "IL-10": self.il10,
            }
        )

        if self.il6 > IL6_STORM_THRESHOLD and self.tnf_alpha > TNF_ALPHA_LETHAL:
            msg = (
                f"[CYTOKINE-STORM] IL-6={self.il6:.1f}, TNF-α={self.tnf_alpha:.1f}. "
                f"Macrophage activation syndrome. Tocilizumab + Anakinra required."
            )
            logger.critical(msg)
            raise CytokineStormDetected(msg)

        if self.il10 < 0.1 * self.il6 and self.il6 > 20:
            logger.warning(
                "IL-10=%.1f << IL-6=%.1f. Anti-inflammatory counter-regulation failing.",
                self.il10,
                self.il6,
            )

        return {
            "IL-6": self.il6,
            "TNF-α": self.tnf_alpha,
            "IL-1β": self.il1_beta,
            "IL-10": self.il10,
        }

    def evaluate_immune_phenotype(self, th1_th2_ratio: float) -> str:
        """Classify the Th1/Th2 immune phenotype."""
        if th1_th2_ratio > 3.0:
            return "[IMMUNE] TH1-dominant. Aggressive intracellular clearance. Autoimmunity risk."
        if th1_th2_ratio < 0.33:
            return "[IMMUNE] TH2-dominant. Humoral defense. Fibrosis risk."
        return "[IMMUNE] Balanced TH1/TH2."


__all__ = ["CytokineStormVector"]
