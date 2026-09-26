"""Vagal tone voltage — SPOF #15 annihilated."""

from __future__ import annotations

import logging

from moac_qmm.constants import HRV_VAGAL_FLOOR

logger = logging.getLogger(__name__)


class VagalToneVoltage:
    """Autonomic nervous system state as modifier for mechanical spasm."""

    def __init__(self, hrv_rmssd: float = 40.0, cortisol_nadir: float = 5.0) -> None:
        self.hrv = hrv_rmssd
        self.cortisol = cortisol_nadir
        self.vagal_integrity = min(1.0, self.hrv / HRV_VAGAL_FLOOR)

    def modify_spasm_probability(self, base_spasm: float) -> float:
        """Amplify or attenuate spasm probability by vagal integrity."""
        if self.vagal_integrity < 0.5:
            amplified = base_spasm * (1.0 + (1.0 - self.vagal_integrity) * 2.0)
            logger.warning(
                "RMSSD=%.1fms. Spasm amplified %.1fx. Cholinergic anti-inflammatory "
                "pathway OFFLINE.",
                self.hrv,
                amplified / max(base_spasm, 0.01),
            )
            return min(1.0, amplified)
        return base_spasm * self.vagal_integrity

    def calc_cholinergic_immune_suppression(self) -> float:
        """Vagus suppresses TNF-α via α7-nAChR. Multiplier on TNF production."""
        if self.vagal_integrity > 0.7:
            return 0.5  # 50% TNF suppression
        if self.vagal_integrity > 0.4:
            return 0.8
        return 1.0  # no suppression


__all__ = ["VagalToneVoltage"]
