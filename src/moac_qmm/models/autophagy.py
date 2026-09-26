"""Autophagy/apoptosis toggle — SPOF #13 annihilated."""

from __future__ import annotations

from moac_qmm.constants import MTOR_AUTOPHAGY_THRESHOLD


class AutophagyApoptosisToggle:
    """mTOR/AMPK ratio determines building vs. demolition mode."""

    def __init__(self, mtor_activity: float = 0.5, ampk_activity: float = 0.5) -> None:
        self.mtor = mtor_activity
        self.ampk = ampk_activity
        self.ratio = mtor_activity / max(0.01, ampk_activity)

    def evaluate_tissue_mode(self) -> tuple[str, float]:
        """Return the tissue mode and the underlying mTOR/AMPK ratio."""
        if self.ratio < MTOR_AUTOPHAGY_THRESHOLD:
            return ("DEMOLITION", self.ratio)
        if self.ratio > 2.0:
            return ("HYPERPLASTIC", self.ratio)
        return ("BUILDING", self.ratio)


__all__ = ["AutophagyApoptosisToggle"]
