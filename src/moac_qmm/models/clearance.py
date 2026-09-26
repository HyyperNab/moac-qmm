"""Renal/hepatic clearance — SPOF #2, #4, #5 annihilated."""

from __future__ import annotations

import logging
from typing import Any

from moac_qmm.constants import (
    ALBUMIN_NORMAL,
    GFR_NORMAL,
    HEPATIC_FLOW_NORMAL,
)

logger = logging.getLogger(__name__)


class RenalHepaticClearance:
    """Total clearance velocity from GFR + hepatic flow + albumin + age."""

    def __init__(
        self,
        gfr: float,
        hepatic_flow: float,
        albumin: float,
        biological_age: int,
    ) -> None:
        self.gfr = gfr
        self.q_h = hepatic_flow
        self.albumin = albumin
        self.bio_age = biological_age

    def calc_total_clearance(self, drug: dict[str, Any]) -> dict[str, float]:
        """Compute total clearance, free fraction, adjusted Vd and t½."""
        renal_clearance = float(drug.get("renal_fraction", 0.3)) * self.gfr / GFR_NORMAL
        extraction_ratio = float(drug.get("hepatic_extraction", 0.3))
        hepatic_clearance = self.q_h * extraction_ratio / HEPATIC_FLOW_NORMAL
        age_penalty = max(0.5, 1.0 - max(0, self.bio_age - 40) * 0.01)
        total_clearance = (renal_clearance + hepatic_clearance) * age_penalty

        bound_fraction = float(drug.get("protein_bound", 0.90))
        albumin_ratio = self.albumin / ALBUMIN_NORMAL
        free_fraction = 1.0 - (bound_fraction * albumin_ratio)
        free_fraction = min(1.0, max(0.01, free_fraction))

        vd_baseline = float(drug.get("vd", 0.5))
        vd_adjusted = vd_baseline * (1.0 + (1.0 - albumin_ratio) * 0.3)
        t_half = (0.693 * vd_adjusted) / max(0.01, total_clearance)

        return {
            "clearance_rate": total_clearance,
            "free_fraction": free_fraction,
            "vd_adjusted": vd_adjusted,
            "t_half": t_half,
            "age_penalty": age_penalty,
            "renal_component": renal_clearance,
            "hepatic_component": hepatic_clearance,
        }

    def evaluate_organ_failure_risk(self) -> str:
        """Screen for organ-failure strata rejections."""
        if self.gfr < 30:
            return (
                "[CLEARANCE-KILL] GFR < 30. Renal failure cascade. "
                "Renally-cleared drugs accumulate to toxic levels."
            )
        if self.q_h < 500:
            return (
                "[CLEARANCE-WARN] Hepatic flow critically low. First-pass metabolism compromised."
            )
        if self.albumin < 2.5:
            return (
                "[CLEARANCE-WARN] Severe hypoalbuminemia. All highly "
                "protein-bound drugs have elevated free fractions."
            )
        return "STABLE"


__all__ = ["RenalHepaticClearance"]
